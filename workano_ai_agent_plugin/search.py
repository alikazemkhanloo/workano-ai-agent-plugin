from xivo_dao.resources.utils.search import SearchConfig
from xivo_dao.resources.utils.search import SearchSystem

from .model import AIAgentModel

ai_agent_config = SearchConfig(
    table=AIAgentModel,
    columns={
        'uuid': AIAgentModel.uuid,
        'created_at': AIAgentModel.created_at,
    },
    default_sort='created_at',
)

ai_agent_search = SearchSystem(ai_agent_config)
