import logging
from .services import AIAgentBusConsumerService

logger = logging.getLogger(__name__)


class AIAgentBusEventHandler:
    def __init__(self, service):
        self.service: AIAgentBusConsumerService = service

    def subscribe(self, bus_consumer):
        bus_consumer.subscribe('application_call_entered', self.application_call_entered)

    def application_call_entered(self, event):
        logger.warning('========>application_call_entered<===========')
        logger.warning(event)
        self.service.application_call_entered(event)
