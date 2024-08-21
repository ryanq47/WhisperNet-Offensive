from redis_om import get_redis_connection, HashModel, Field
from modules.config import Config
from modules.log import log
from typing import Any, Dict, Optional

logger = log(__name__)


redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)

if redis:
    logger.debug("Redis connection successful")


from redis_om import JsonModel, Field
from typing import List, Dict, Optional


class PowerShellKeyModel(JsonModel):
    executable: Optional[str] = None
    command: Optional[str] = None
    id: Optional[int] = None
    somedata: Optional[str] = None


class FormJModel(JsonModel):
    rid: str = Field(index=True, primary_key=True) # use RID as primary key. these are all unique
    data: Dict[str, Any] = Field(default_factory=dict)  # temp basic dict
    message: str
    status: int
    timestamp: int

    class Meta:
        database = redis  # The Redis connection
        #global_key_prefix = "FormJ"


if __name__ == "__main__":
    formj_message = FormJModel(
        message="SomeMessage",
        rid="489d3491-c950-4cb8-b485-7dfb1f1aa223",
        status=200,
        timestamp=1234567890,
        data={
            "Powershell": [
                SyncKey(
                    executable="ps.exe", command="net user /domain add bob", id=1234
                ),
                SyncKey(
                    executable="ps.exe",
                    command="net group /add Domain Admins Bob",
                    id=1235,
                ),
            ],
            "SomeSync": [SyncKey(somedata="somedata"), SyncKey(somedata="somedata")],
        },
        error={"message": None, "aid": [None, None], "rid": None},
    )

    formj_message.save()

    # use rid to get the request id. Note, redis doesnt track uniqueness, and has auto prim keys, sooo this better actually be unique.
    retrieved_message = FormJModel.get("489d3491-c950-4cb8-b485-7dfb1f1aa223")
    print(retrieved_message.data)
