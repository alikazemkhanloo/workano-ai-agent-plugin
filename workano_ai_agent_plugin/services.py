import logging
logger = logging.getLogger(__name__)



class AIAgentBusConsumerService():
    def __init__(self, ari):
        self.ari = ari

    def application_call_entered(self, event):
        print('call entered >>> event: ', event)
        channel_id = event.get('call',{}).get('id')
        application_uuid = event.get('application_uuid')
        if application_uuid == '1ef1a021-0caa-477c-bc19-764cd65a8a87':
            # channel = self.ari.channels.get(channelId=channel_id)
            request = {
                'app': f'wazo-app-{application_uuid}',
                "external_host": '127.0.0.1:4000',
                "format":'slin16',
                "direction":'both'

            }
            # Create external media channel and bridge it with the current call
            external = self.ari.channels.externalMedia(**request)

            # Optionally bridge it to the main channel
            self.ari.bridges.create(type='mixing')
            bridge = self.ari.bridges.list()[-1]  # or better, store it
            bridge.addChannel(channel=f"{channel_id},{external.id}")

            print(f"Connected call {channel_id} to external media {external.id}")


def build_ai_agent_bus_consumer_service(ari):
    return AIAgentBusConsumerService(ari)

