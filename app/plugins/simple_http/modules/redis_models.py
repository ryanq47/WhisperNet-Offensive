from redis_om import get_redis_connection, HashModel, Field, JsonModel
from modules.config import Config
from modules.log import log
from typing import Any, Dict, Optional
from typing import List, Dict, Optional

logger = log(__name__)


redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)

if redis:
    logger.debug("Redis connection successful")

class FormJModel(JsonModel):
    rid: str = Field(index=True, primary_key=True) # use RID as primary key. these are all unique
    data: Dict[str, Any] = Field(default_factory=dict)  # temp basic dict
    message: str
    status: int
    timestamp: int

    class Meta:
        database = redis  # The Redis connection
        #global_key_prefix = "FormJ"

    @classmethod
    def set_prefix(cls, prefix: str):
        """
        Set a dynamic prefix for the model.
        
        can either be request or response in this case
        """
        cls.Meta.global_key_prefix = prefix

