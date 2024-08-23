from flask import jsonify, request
from modules.instances import Instance
from modules.log import log
from plugins.simple_http.modules.redis_models import FormJModel
import json
from redis_om import get_redis_connection, HashModel
from modules.utils import api_response
from plugins.simple_http.modules.redis_queue import RedisQueue
from flask_jwt_extended import jwt_required

logger = log(__name__)
app = Instance().app


class Info:
    name = "simple_http"
    author = "ryanq.47"

# for queuing commands. Should be protected endpoint
@app.route("/command/<client_id>", methods=["POST"])
@jwt_required()
def simple_http_queue_command(client_id):
    try:
        # get data from req
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

        logger.debug(f"RID: {dict_data.get('rid')}")
        formj_message = FormJModel(
            rid=dict_data.get("rid"),
            data=dict_data.get("data", {}),
            message=dict_data.get("message", ""),
            status=dict_data.get("status", 0),
            timestamp=dict_data.get("timestamp", 0),
        )

        formj_message.save()

        rid = dict_data.get("rid")

        # set up queue
        queue = RedisQueue(
            client_id = client_id
        )
        # enque this request ID to client queue
        queue.enqueue(
            item=rid
        )

        return api_response(
            status = 200,
            message="Command queued successfully"
        )

    except Exception as e:
        import traceback

        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())  # This will print the full stack trace
        return api_response(message="Internal server error", status=500)



# Optional route example
@app.route("/get/<client_id>", methods=["GET"])
def simple_http_get(client_id):
    return jsonify({"client_id": f"{client_id}"})

    # for queue, create a key with a queue, named the name of the client id?

    # then pop command from queue


# for storing responses
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

        formj_message.save()

        # retrieved_message = FormJModel.get(dict_data.get("rid"))
        # logger.debug(retrieved_message)

        #rid = dict_data.get("rid")

        # WORKS! yay. now figuroe out waht we even fucing need here
        # need to store message in 

        #try:
            # Assuming `rid` is unique, this query should return the correct instance
        #    retrieved_message = FormJModel.get(rid)
        #    if not retrieved_message:
        #        logger.debug("Could not find")
        #        # raise NotFoundError
        #except Exception as e:
        #    print(f"Entry with rid {rid} not found in Redis: {e}")
        #    # Handle the case where the entry is not found
        #    return jsonify({"client_id": "client_id"}), 500


        #return jsonify({"client_id": "client_id"}), 200
        return api_response(
            status = 200,
            message="Request stored successfully"
        )

    except Exception as e:
        import traceback

        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())  # This will print the full stack trace
        return api_response(message="Internal server error", status=500)
