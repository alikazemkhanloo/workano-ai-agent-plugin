import logging
from functools import wraps
from wazo_confd.helpers.restful import ItemResource, ListResource

from .model import AIAgentModel
from .schema import AIAgentSchema

from flask import url_for, request
from wazo_confd.auth import required_acl

class AIAgentListResource(ListResource):
    schema = AIAgentSchema
    model = AIAgentModel

    def build_headers(self, model):
        return {'Location': url_for('ai-agent-list', _external=True)}

    @required_acl('calld.ai-agent.config.read')
    def get(self):
        return super().get()

    @required_acl('calld.ai-agent.config.create')
    def post(self):
        return super().post()
    




class AIAgentItemResource(ItemResource):
    schema = AIAgentSchema
    model = AIAgentModel

    def build_headers(self, model):
        return {'Location': url_for('ai-agent-item', uuid=model.uuid, _external=True)}


    @required_acl('calld.ai-agent.config.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('calld.ai-agent.config.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('calld.ai-agent.config.delete')
    def delete(self, uuid):
        return super().delete(uuid)