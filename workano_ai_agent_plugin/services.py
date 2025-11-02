
from .dao import AIAgentDao
import logging
logger = logging.getLogger(__name__)



class AIAgentBusConsumerService():
    def __init__(self, dao, ari):
        self.dao = dao
        self.ari = ari

    def application_call_entered(self, event):
        print('call entered >>> event: ', event)
        call_id = event.get('call_id')
        application_uuid = event.get('application_uuid')
        channel = self.ari.channels.get(channelId=call_id)
        request = {
            'app': f'wazo-app-{application_uuid}',
            "external_host": 'my-ai-server:4000',
            "format":'slin16',
            "direction":'both'

        }

        return channel.externalMedia(**request)


def build_ai_agent_bus_consumer_service(ari):
    dao = AIAgentDao()
    return AIAgentBusConsumerService(dao, ari,)

