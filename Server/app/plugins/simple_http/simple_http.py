import json
import time
import traceback

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from redis_om import get_redis_connection, HashModel, NotFoundError
from redis.commands.json.path import Path

from modules.instances import Instance
from modules.log import log
from modules.utils import api_response
from modules.audit import Audit
from modules.form_j import FormJ
from modules.redis_models import Client
from modules.config import Config
from plugins.simple_http.modules.redis_models import FormJModel
from plugins.simple_http.modules.redis_queue import RedisQueue


logger = log(__name__)
app = Instance().app

redis = get_redis_connection(  # switch to config values
    host=Config().config.redis.bind.ip,
    port=Config().config.redis.bind.port,
    decode_responses=True,  # Ensures that strings are not returned as bytes
)

class Info:
    name = "simple_http"
    author = "ryanq.47"

# for queuing commands. Should be protected endpoint
@app.route("/command/<client_id>", methods=["POST"])
@jwt_required()
def simple_http_queue_command(client_id):
    try:
        # set prefix
        FormJModel.set_prefix("request")

        # get data from req
        dict_data = request.get_json()
        if dict_data is None:
            return api_response(message="No data in request", status=400)

        # create a form j object, and parse it, which retuns a munch object
        fj = FormJ(dict_data).parse()
        # enter those values into the model for redis
        formj_message = FormJModel(
            rid=fj.rid,
            data=fj.data,
            message=fj.message,
            status=fj.status,
            timestamp=fj.timestamp,
        )
        logger.debug(f"COMMAND: RID: {fj.rid}")
        # save to redis
        formj_message.save()

        # set up queue
        queue = RedisQueue(
            client_id = client_id
        )
        # enque this request ID to client queue
        queue.enqueue(
            item=fj.rid
        )

        # Audit command
        user_identity = get_jwt_identity()
        dict_data.setdefault('audit', {})  # Ensure 'audit' key exists in dict_data
        dict_data['audit']['user_identity'] = user_identity  # Add user identity to the log

        a = Audit()
        a.audit(dict_data)

        return api_response(
            status = 200,
            message="Command queued successfully"
        )

    except KeyError as ke:
        return api_response(message="Invalid or missing Key", status=400)

    except TypeError as e:
        return api_response(message="Invalid data type in key", status=400)

    except Exception as e:
        import traceback

        logger.error(f"An error occurred: {e}")
        #logger.error(traceback.format_exc())  # This will print the full stack trace
        return api_response(message="Internal server error", status=500)


@app.route("/response/<response_id>", methods=["GET"])
@jwt_required()
def simple_http_get_response(response_id):
    # okay, for whatever reason, the redis-om model FormJModel is not working with this, it spits a key not found error, so I'm doing it manually.
    try:
        key = f"response:plugins.simple_http.modules.redis_models.FormJModel:{response_id}"

        # grab the entire json object stored at the given key in Redis
        response_redis = redis.json().get(key, Path.root_path())

        # for some reason this is not getting the item/not finding it
        if response_redis == None:
            # Handle the case where the response does not exist
            return api_response(
                status=404,
                message="Response not found"
           )

        # Pull data out - up to debate for whether to send the whole message in data, or just pull the data out
        rid = response_redis.get("rid")
        data = response_redis.get("data")

        # Send back to requester
        return api_response(
            rid=rid,
            data=data
        )

    except Exception as e:
        # Log the exception with traceback
        #logger.error(traceback.format_exc())
        logger.error(e)
        return api_response(
            status=500,
            message="Internal server error"
        )

@app.route("/get/<client_id>", methods=["GET"])
def simple_http_get(client_id):
    #return jsonify({"client_id": f"{client_id}"})

    try:
        # set prefix to request, to make sure that we are only
        # getting keys with the request prefix
        FormJModel.set_prefix("request")

        # this will check for non alphanum and - chars.
        rq = RedisQueue(
            client_id = client_id
        )

        # find queue with that client id
        # pop command 
        rid_of_command = rq.dequeue()

        logger.debug("Popping next in queue")
        logger.debug(rid_of_command)

    
        # this may be the same bug as b4. 
        if not rid_of_command:
            logger.warning(f"Queue empty for client: {client_id}")
            
            # switchign to a nothing command
            return api_response()

        # look up command rid basedon popped command
        # get json from redis

        command = FormJModel.get(rid_of_command)
        
        # Convert from redis key to dict, then use formj for validation N stuff
        command_dict = FormJ(dict(command)).parse()

        # adding/updating client in redis
        client = Client(type="simple-http", client_id=client_id, checkin=int(time.time()))
        client.save()

        # send back to client - WITH rid
        return api_response(
            data=command_dict.data,
            rid=rid_of_command
        )
        

    # dooo I keep raising errors up the stack?
    except NotFoundError:
        # Handle the case where the command is not found
        logger.error(f"No command found with RID: {rid_of_command}")
        return api_response(status=404)
        
    except ValueError as e:
        logger.error(e)
        return api_response(status=400)
        
    except Exception as e:

        logger.error(e)
        return api_response(status=500)


# for storing responses
@app.route("/post/<client_id>", methods=["POST"])
def simple_http_post(client_id):
    try:
        FormJModel.set_prefix("response")

        dict_data = request.get_json()
        if dict_data is None:
            return api_response(message="No data in request", status=400)

        # create a form j object, and parse it, which retuns a munch object
        fj = FormJ(dict_data).parse()
        # enter those values into the model for redis
        formj_message = FormJModel(
            rid=fj.rid,
            data=fj.data,
            message=fj.message,
            status=fj.status,
            timestamp=fj.timestamp,
        )
        #logger.debug(f"POST: RID: {fj.rid}")

        # write to redis
        formj_message.save()

       # adding client to redis
        client = Client(type="simple-http", client_id=client_id, checkin=int(time.time()))
        client.save()

        return api_response(
            status = 200,
            message="Request stored successfully"
        )

    except KeyError as ke:
        return api_response(message="Invalid or missing Key", status=400)

    except TypeError as e:
        return api_response(message="Invalid data type in key", status=400)

    except Exception as e:
        import traceback

        logger.error(f"An error occurred: {e}")
        #logger.error(traceback.format_exc())  # This will print the full stack trace
        return api_response(message="Internal server error", status=500)

