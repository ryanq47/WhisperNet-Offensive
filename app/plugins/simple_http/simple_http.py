from flask import jsonify, request
from modules.instances import Instance
from modules.log import log
from plugins.simple_http.modules.redis_models import FormJModel, PowerShellKeyModel
import json
from redis_om import get_redis_connection, HashModel, Field
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
        dict_data = request.get_json()  # gets request and turns into json

        if dict_data == None:
            return api_response(message="No data in request", status=400)

        client_id = dict_data.get("rid", None)

        # if these == none... reutrn failed 400

        # formj_message = FormJModel(response.text)
        # depack dict for values for FormJModel

        ## Redis stuff causing issues, nonetype not subscriptable.
        ## Go learn redis first then come back to this
        # formj_message = FormJModel(**dict_data)

        # Save it to Redis
        # formj_message.save()

        # retrieved_message = FormJModel.get(client_id)
        # logger.debug(retrieved_message)
        # if retrieved_message is None:
        #    return api_response(message="Failed to retrieve saved message", status=500)

        # Retrieve it using the rid
        ##retrieved_message = FormJModel.get(dict_data.get("rid", None))
        # print(retrieved_message)
        # return jsonify({"client_id": f"{client_id}"})
        # replace w api_response
        return jsonify({"client_id": client_id}), 200

    except Exception as e:
        logger.debug(f"Request: {request if request else ''}")
        logger.error(e)
        return api_response(status=500, message="")


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
