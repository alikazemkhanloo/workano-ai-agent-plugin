import logging

from workano_ai_agent_plugin.bus_consume import AIAgentBusEventHandler
from .db import init_db
from .services import build_ai_agent_bus_consumer_service
# from .bus_consume import AIAgentBusEventHandler

logger = logging.getLogger(__name__)

class Plugin:
    def load(self, dependencies):
        logger.info('workano_ai_agent_plugin is loading')
        api = dependencies['api']
        ari = dependencies['ari']
        config = dependencies['config']
        init_db('postgresql://asterisk:proformatique@localhost/asterisk?application_name=workano_ai_agent_plugin')


        # events
        bus_consumer = dependencies['bus_consumer']
        ai_agent_bus_consumer_service = build_ai_agent_bus_consumer_service(ari)
        bus_event_handler = AIAgentBusEventHandler(ai_agent_bus_consumer_service)

        # # Subscribe to bus events
        bus_event_handler.subscribe(bus_consumer)

    def unload(self):
        pass
