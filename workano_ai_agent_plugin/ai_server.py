
import asyncio
import socket
import os
from aiortc import RTCPeerConnection, MediaStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaRecorder
import aiohttp
import numpy as np
import soundfile as sf

# UDP server to receive RTP from Asterisk
UDP_IP = "0.0.0.0"
UDP_PORT = 4000

# OpenAI Realtime endpoint
OPENAI_MODEL = "gpt-realtime"
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")


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
        pcm_chunk = await self.queue.get()
        # Convert PCM16 bytes into AudioFrame
        from av import AudioFrame
        frame = AudioFrame(format="s16", layout="mono", samples=len(pcm_chunk)//2)
        frame.planes[0].update(pcm_chunk)
        frame.sample_rate = SAMPLE_RATE
        return frame

async def main():
    # Queue to pass audio from UDP → WebRTC track
    import asyncio
    audio_queue = asyncio.Queue()

    # 1️⃣ Start UDP server to receive RTP from Asterisk
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for RTP from Asterisk on {UDP_IP}:{UDP_PORT}")
    asterisk_addr = None

    async def forward_ai_audio(track, udp_sock, udp_ip, udp_port):
        """
        Reads audio frames from OpenAI remote track and sends as PCM to Asterisk
        """
        while True:
            frame = await track.recv()  # frame is an AudioFrame
            # Convert AudioFrame to PCM16 bytes
            pcm_bytes = frame.planes[0].to_bytes()
            # Send to Asterisk via UDP (same port as externalMedia)
            if asterisk_addr:
                udp_sock.sendto(pcm_bytes, asterisk_addr)
            else:
                print('no asterisk addr')

    async def udp_listener():
        nonlocal asterisk_addr
        while True:
            data, addr = await asyncio.get_event_loop().sock_recv(sock, 2048)
            if asterisk_addr is None:
                asterisk_addr = addr  # remember where RTP is coming from
            print(f"Asterisk RTP address detected: {asterisk_addr}")

            # data is raw PCM from externalMedia
            await audio_queue.put(data)

    asyncio.create_task(udp_listener())

    # 2️⃣ Create WebRTC peer connection to OpenAI
    pc = RTCPeerConnection()
    pc.addTrack(AsteriskAudioTrack(audio_queue))

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            asyncio.create_task(forward_ai_audio(track, sock, UDP_IP, UDP_PORT))


    # 3️⃣ Capture AI audio from OpenAI Realtime API
    async def consume_ai_audio(track):
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            frame = await track.recv()
            # Convert AudioFrame to PCM16 bytes
            pcm_bytes = frame.planes[0].to_bytes()
            sock_out.sendto(pcm_bytes, (UDP_IP, UDP_PORT))  # send back to Asterisk
    # You will attach this when OpenAI track arrives

    # 4️⃣ Create offer and send SDP to OpenAI Realtime API
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    sdp = offer.sdp

    # Use ephemeral token or standard API key
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/sdp"}
        async with session.post("https://api.openai.com/v1/realtime/calls", data=sdp, headers=headers) as resp:
            answer_sdp = await resp.text()

    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer_sdp, type="answer"))

    print("WebRTC connected to OpenAI Realtime API")

    # 5️⃣ Wait forever
    await asyncio.Future()

asyncio.run(main())
