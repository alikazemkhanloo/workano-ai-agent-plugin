from sqlalchemy import (
    Column
)
from sqlalchemy import text, func
from sqlalchemy.types import (String, Boolean, DateTime, Text, Integer)
from xivo_dao.helpers.db_manager import UUIDAsString
from sqlalchemy.types import JSON
from sqlalchemy_utils import UUIDType, generic_repr

from .db import Base
@generic_repr
class AIAgentModel(Base):
    __tablename__ = 'plugin_ai_agent_config'
    uuid = Column(UUIDAsString(36), primary_key=True,
                  server_default=text('uuid_generate_v4()'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
