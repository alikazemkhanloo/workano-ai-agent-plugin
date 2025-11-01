
from .dao import AIAgentDao
import logging
from wazo_confd.helpers.resource import CRUDService
from .validator import build_ai_agent_validator
from .notifier import build_ai_agent_notifier
logger = logging.getLogger(__name__)

class AIAgentService(CRUDService):
    pass


def build_ai_agent_service():
    dao = AIAgentDao()
    return AIAgentService(dao, build_ai_agent_validator(), build_ai_agent_notifier())



class AIAgentBusConsumerService():
    def __init__(self, dao):
        self.dao = dao


def build_ai_agent_bus_consumer_service():
    dao = AIAgentDao()
    return AIAgentBusConsumerService(dao)

