from flask import jsonify, request
from modules.instances import Instance
from modules.log import log
from plugins.simple_http.modules.redis_models import FormJModel, PowerShellKeyModel
import json
from redis_om import get_redis_connection, HashModel
from modules.utils import api_response

logger = log(__name__)
app = Instance().app


class Info:
    name = "simple_http"
    author = "ryanq.47"


# Optional route example
@app.route("/get/<client_id>", methods=["GET"])
def simple_http_get(client_id):
    return jsonify({"client_id": f"{client_id}"})


@app.route("/post/<client_id>", methods=["POST"])
def simple_http_post(client_id):
    try:
        dict_data = request.get_json()
        if dict_data is None:
            return api_response(message="No data in request", status=400)

        # Ensure the necessary keys are present in the dict_data
        required_keys = ["rid", "data", "message", "status", "timestamp"]
        for key in required_keys:
            if key not in dict_data:
                logger.error(f"Missing required field: {key}")
                return api_response(
                    message=f"Missing required field: {key}", status=400
                )

        # Addtl validation for input data types
        if not isinstance(dict_data.get("rid"), str):
            logger.error("Invalid type for 'rid'")
            return api_response(message="Invalid type for 'rid'", status=400)

        if not isinstance(dict_data.get("status"), int):
            logger.error("Invalid type for 'status'")
            return api_response(message="Invalid type for 'status'", status=400)

        if not isinstance(dict_data.get("timestamp"), int):
            logger.error("Invalid type for 'timestamp'")
            return api_response(message="Invalid type for 'timestamp'", status=400)

        if not isinstance(dict_data.get("data"), dict):
            logger.error("Invalid type for 'data'")
            return api_response(message="Invalid type for 'data'", status=400)

        # Error lies in here
        # Unpack the dict_data into the FormJModel, handling potential missing data
        logger.debug(f"RID: {dict_data.get('rid')}")
        formj_message = FormJModel(
            rid=dict_data.get("rid"),
            data=dict_data.get("data", {}),
            message=dict_data.get("message", ""),
            status=dict_data.get("status", 0),
            timestamp=dict_data.get("timestamp", 0),
        )

        # logger.debug(formj_message)

        formj_message.save()

        # retrieved_message = FormJModel.get(dict_data.get("rid"))
        # logger.debug(retrieved_message)

        rid = dict_data.get("rid")

        # WORKS! yay. now figuroe out waht we even fucing need here

        try:
            # Assuming `rid` is unique, this query should return the correct instance
            retrieved_message = FormJModel.get(rid)
            if not retrieved_message:
                logger.debug("Could not find")
                # raise NotFoundError
        except Exception as e:
            print(f"Entry with rid {rid} not found in Redis: {e}")
            # Handle the case where the entry is not found
            return jsonify({"client_id": "client_id"}), 500


        return jsonify({"client_id": "client_id"}), 200

    except Exception as e:
        import traceback

        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())  # This will print the full stack trace
        return api_response(message="Internal server error", status=500)


"""
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

"""
