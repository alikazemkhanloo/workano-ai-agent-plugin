import logging
from .db import init_db
from .services import build_ai_agent_service
from .resource import AIAgentListResource, AIAgentItemResource
# from .bus_consume import AIAgentBusEventHandler

logger = logging.getLogger(__name__)

class Plugin:
    def load(self, dependencies):
        logger.info('workano_ai_agent_plugin is loading')
        api = dependencies['api']
        config = dependencies['config']
        init_db('postgresql://asterisk:proformatique@localhost/asterisk?application_name=workano_ai_agent_plugin')
        ai_agent_service = build_ai_agent_service()


        # events
        # bus_consumer = dependencies['bus_consumer']
        # ai_agent_bus_consumer_service = build_ai_agent_bus_consumer_service()
        # bus_event_handler = AIAgentBusEventHandler(ai_agent_bus_consumer_service)

        # # Subscribe to bus events
        # bus_event_handler.subscribe(bus_consumer)

        api.add_resource(
            AIAgentListResource,
            '/ai-agent',
            endpoint='ai-agent-list',
            resource_class_args=(ai_agent_service,)
        )
        api.add_resource(
            AIAgentItemResource,
            '/ai-agent/<uuid>',
            endpoint='ai-agent-item',
            resource_class_args=(ai_agent_service,)
        )

    def unload(self):
        pass
