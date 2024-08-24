from flask import jsonify, request
from modules.instances import Instance
from modules.log import log
from plugins.simple_http.modules.redis_models import FormJModel
import json
from redis_om import get_redis_connection, HashModel, NotFoundError
from modules.utils import api_response
from plugins.simple_http.modules.redis_queue import RedisQueue
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.audit import Audit
import traceback
from modules.form_j import FormJ

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

# Optional route example
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

        if not rid_of_command:
            logger.warning(f"Queue empty for rid: {client_id}")
            return api_response(
                status=202, # sending a 204 no content
                message = "Queue empty or does not exist"
            )

        # look up command rid basedon popped command
        # get json from redis
        # do I need to set prefix here?
        # testing shows that it's fine and returns the correct messag
        command = FormJModel.get(rid_of_command)
        

        # Convert from redis key to dict, then use formj for validation N stuff
        command_dict = FormJ(dict(command)).parse()

        # need a bit of thinking here, do we send back the SAME rid? or just a new one.
        # mainly trying to track responses
        # For now just leaving it.

        # send back to client
        return api_response(
            data=command_dict.data
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
        # Print the complete traceback
        traceback.print_exc()  # This will print the full traceback to stderr
        logger.error(traceback.format_exc())  # Log the traceback as a string
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

        # write to redis
        formj_message.save()

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

