
import asyncio
import socket
import os
import logging
from aiortc import RTCPeerConnection, MediaStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaRecorder
import aiohttp
import json
import numpy as np
import soundfile as sf

# UDP server to receive RTP from Asterisk
UDP_IP = "0.0.0.0"
UDP_PORT = 4000

# OpenAI Realtime endpoint
OPENAI_MODEL = "gpt-realtime"
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("workano.ai_server")


# PCM parameters
SAMPLE_RATE = 8000
CHANNELS = 1

class AsteriskAudioTrack(MediaStreamTrack):
    """
    This track feeds audio from Asterisk into OpenAI Realtime API
    """
    kind = "audio"

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    async def recv(self):
        # Wait for next chunk from queue
        logger.debug("AsteriskAudioTrack waiting for next PCM chunk from queue")
        pcm_chunk = await self.queue.get()
        logger.debug("AsteriskAudioTrack received PCM chunk of %d bytes", len(pcm_chunk))
        # Convert PCM16 bytes into AudioFrame
        from av import AudioFrame
        frame = AudioFrame(format="s16", layout="mono", samples=len(pcm_chunk)//2)
        frame.planes[0].update(pcm_chunk)
        frame.sample_rate = SAMPLE_RATE
        logger.debug("AsteriskAudioTrack created AudioFrame with %d samples", frame.samples)
        return frame

async def main():
    # Queue to pass audio from UDP → WebRTC track
    import asyncio
    audio_queue = asyncio.Queue()

    logger.info("Starting ai_server main")

    if not OPENAI_KEY:
        logger.warning("OPENAI_API_KEY is not set. Requests to OpenAI will fail unless provided.")

    # 1️⃣ Start UDP server to receive RTP from Asterisk
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    logger.info("Listening for RTP from Asterisk on %s:%d", UDP_IP, UDP_PORT)
    asterisk_addr = None

    async def forward_ai_audio(track, udp_sock, udp_ip, udp_port):
        """
        Reads audio frames from OpenAI remote track and sends as PCM to Asterisk
        """
        logger.info("forward_ai_audio task started")
        while True:
            try:
                frame = await track.recv()  # frame is an AudioFrame
                logger.debug("forward_ai_audio received audio frame")
                # Convert AudioFrame to PCM16 bytes
                pcm_bytes = frame.planes[0].to_bytes()
                # Send to Asterisk via UDP (same port as externalMedia)
                if asterisk_addr:
                    udp_sock.sendto(pcm_bytes, asterisk_addr)
                    logger.debug("Sent %d bytes of AI audio to Asterisk at %s", len(pcm_bytes), asterisk_addr)
                else:
                    logger.debug("No asterisk_addr yet, dropping AI audio frame")
            except Exception as e:
                logger.exception("Error in forward_ai_audio: %s", e)
                await asyncio.sleep(0.1)

    async def udp_listener():
        nonlocal asterisk_addr
        logger.info("Starting udp_listener task to receive RTP from Asterisk")
        while True:
            try:
                # asyncio.get_event_loop().sock_recv returns bytes only (no address).
                # Use blocking recvfrom in a threadpool so we get (data, addr).
                loop = asyncio.get_event_loop()
                data, addr = await loop.run_in_executor(None, sock.recvfrom, 2048)
                if asterisk_addr is None:
                    asterisk_addr = addr  # remember where RTP is coming from
                    logger.info("Asterisk RTP address detected: %s", asterisk_addr)
                else:
                    logger.debug("Received RTP datagram from %s (asterisk_addr=%s)", addr, asterisk_addr)

                # data is raw PCM from externalMedia
                await audio_queue.put(data)
                logger.debug("Enqueued PCM chunk of %d bytes into audio_queue", len(data))
            except Exception as e:
                logger.exception("Error in udp_listener: %s", e)
                await asyncio.sleep(0.1)

    asyncio.create_task(udp_listener())
    logger.info("UDP listener task scheduled")

    # 2️⃣ Create WebRTC peer connection to OpenAI
    logger.info("Creating RTCPeerConnection to OpenAI")
    pc = RTCPeerConnection()
    track = AsteriskAudioTrack(audio_queue)
    pc.addTrack(track)
    logger.info("Added AsteriskAudioTrack to PeerConnection")

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            logger.info("Received remote track of kind=audio from OpenAI")
            asyncio.create_task(forward_ai_audio(track, sock, UDP_IP, UDP_PORT))


    # 3️⃣ Capture AI audio from OpenAI Realtime API
    async def consume_ai_audio(track):
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info("consume_ai_audio task started")
        while True:
            try:
                frame = await track.recv()
                logger.debug("consume_ai_audio received audio frame")
                # Convert AudioFrame to PCM16 bytes
                pcm_bytes = frame.planes[0].to_bytes()
                sock_out.sendto(pcm_bytes, (UDP_IP, UDP_PORT))  # send back to Asterisk
                logger.debug("Sent %d bytes of AI audio to %s:%d via separate socket", len(pcm_bytes), UDP_IP, UDP_PORT)
            except Exception as e:
                logger.exception("Error in consume_ai_audio: %s", e)
                await asyncio.sleep(0.1)
    # You will attach this when OpenAI track arrives

    # 4️⃣ Create offer and send SDP to OpenAI Realtime API
    logger.info("Creating offer and setting local description")
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    sdp = offer.sdp

    # Use ephemeral token or standard API key
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
        url = "https://api.openai.com/v1/realtime/calls"

        # Build session configuration as JSON per OpenAI example
        session_config = {
            "type": "realtime",
            "model": OPENAI_MODEL,
            "audio": {"output": {"voice": "marin"}},
        }

        logger.info("Sending SDP offer to OpenAI realtime endpoint (model=%s)", OPENAI_MODEL)

        # Send multipart/form-data with fields 'sdp' and 'session' (JSON string)
        form = aiohttp.FormData()
        form.add_field("sdp", sdp)
        form.add_field("session", json.dumps(session_config), content_type="application/json")

        async with session.post(url, data=form, headers=headers) as resp:
            status = resp.status
            answer_sdp = await resp.text()
            logger.info("OpenAI realtime endpoint responded with status %s", status)
            if status != 200:
                # Try to parse structured JSON error if present, otherwise log raw body
                try:
                    err = await resp.json()
                except Exception:
                    err = answer_sdp
                logger.error("Failed to get SDP answer from OpenAI: status=%s body=%s", status, err)
                raise RuntimeError(f"OpenAI realtime endpoint returned status {status}")

    # Only set remote description when we have a valid SDP answer (status 200)
    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer_sdp, type="answer"))
    logger.info("Set remote description from OpenAI answer")

    logger.info("WebRTC connected to OpenAI Realtime API")

    # 5️⃣ Wait forever
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        logger.info("Main task cancelled, shutting down")
    finally:
        logger.info("Cleaning up PeerConnection")
        await pc.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("Unhandled exception in ai_server main")
