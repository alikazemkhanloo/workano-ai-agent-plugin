import logging

from .bus_consume import AIAgentBusEventHandler
from .services import build_ai_agent_bus_consumer_service

logger = logging.getLogger(__name__)

class Plugin:
    def load(self, dependencies):
        logger.info('workano_ai_agent_plugin is loading')
        ari = dependencies['ari']

        # events
        bus_consumer = dependencies['bus_consumer']
        ai_agent_bus_consumer_service = build_ai_agent_bus_consumer_service(ari.client)
        bus_event_handler = AIAgentBusEventHandler(ai_agent_bus_consumer_service)

        # # Subscribe to bus events
        bus_event_handler.subscribe(bus_consumer)

    def unload(self):
        pass
