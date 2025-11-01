from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin
from xivo_dao.resources.utils.search import SearchResult

from .model import AIAgentModel
from .dao_base import expunge_result


class AIAgentPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = AIAgentModel

    def __init__(self, session, ai_agent_search, tenant_uuids=None):
        self.session = session
        self.search_system = ai_agent_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(AIAgentModel)
        # query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def create(self, model):
        self.session.add(model)
        try:
            self.session.flush()
        except Exception:
            pass

        expunge_result(self.session, model)
        return model

    def get_by(self, criteria):
        res = super().get_by(criteria)
        expunge_result(self.session, res)
        return res

    def find_by(self, criteria):
        res = super().find_by(criteria)
        expunge_result(self.session, res)
        return res

    def find_all_by(self, criteria):
        res = super().find_all_by(criteria)
        expunge_result(self.session, res)
        return res

    def search(self, parameters):
        res: SearchResult = super().search(parameters)
        expunge_result(self.session, res.items)
        return res
    
    def edit(self, model):
        try:
            self.session.merge(model)
        except Exception:
            self.persist(model)
