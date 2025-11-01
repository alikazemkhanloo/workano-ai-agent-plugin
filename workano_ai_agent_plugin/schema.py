import os
from marshmallow import fields, validates, ValidationError, validates_schema
from wazo_confd.helpers.mallow import BaseSchema
from xivo.mallow.validate import Length, OneOf, Range, Regexp

class AIAgentListRequestSchema(BaseSchema):
    pass

class AIAgentItemRequestSchema(BaseSchema):
    pass

class AIAgentSchema(BaseSchema):
    uuid = fields.String()
