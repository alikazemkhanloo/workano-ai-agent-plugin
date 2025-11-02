import logging
logger = logging.getLogger(__name__)



class AIAgentBusConsumerService():
    def __init__(self, ari):
        self.ari = ari

    def application_call_entered(self, event):
        print('call entered >>> event: ', event)
        call_id = event.get('call_id')
        application_uuid = event.get('application_uuid')
        if application_uuid == '1ef1a021-0caa-477c-bc19-764cd65a8a87':
            channel = self.ari.channels.get(channelId=call_id)
            request = {
                'app': f'wazo-app-{application_uuid}',
                "external_host": '127.0.0.1:4000',
                "format":'slin16',
                "direction":'both'

            }
            return channel.externalMedia(**request)


def build_ai_agent_bus_consumer_service(ari):
    return AIAgentBusConsumerService(ari)

