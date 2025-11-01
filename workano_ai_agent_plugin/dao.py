from .persistor import AIAgentPersistor
from .search import ai_agent_search
from .model import AIAgentModel
from .dao_base import BaseDAO


class AIAgentDAO(BaseDAO):
    def _persistor(self, session, tenant_uuids=None):
        return AIAgentPersistor(session, ai_agent_search, tenant_uuids)

    def search(self, tenant_uuids=None, **parameters):
        with self.new_session() as s:
            return self._persistor(s, tenant_uuids).search(parameters)

    def get(self, uuid, tenant_uuids=None):
        with self.new_session() as s:
            return self._persistor(s, tenant_uuids).get_by({'uuid': uuid})

    def get_by(self, tenant_uuids=None, **criteria) -> AIAgentModel:
        with self.new_session() as s:
            return self._persistor(s, tenant_uuids).get_by(criteria)

    def find(self, uuid, tenant_uuids=None):
        with self.new_session() as s:
            return self._persistor(s, tenant_uuids).find_by({'uuid': uuid})

    def find_by(self, tenant_uuids=None, **criteria):
        with self.new_session() as s:
            return self._persistor(s, tenant_uuids).find_by(criteria)

    def find_all_by(self, tenant_uuids=None, **criteria):
        with self.new_session() as s:
            return self._persistor(s, tenant_uuids).find_all_by(criteria)

    def create(self, model_instance):
        with self.new_session() as s:
            return self._persistor(s).create(model_instance)

    def edit(self, model_instance):
        with self.new_session() as s:
            return self._persistor(s).edit(model_instance)

    def delete(self, model_instance):
        with self.new_session() as s:
            return self._persistor(s).delete(model_instance)
