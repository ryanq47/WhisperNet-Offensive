from flask import jsonify, request
from modules.instances import Instance
from modules.log import log
from flask_jwt_extended import jwt_required, get_jwt_identity
from plugins.ftp_server.modules.ftp import LeFTPServer
from modules.instances import Instance
from threading import Thread
from modules.utils import api_response
from modules.config import Config

logger = log(__name__)
app = Instance().app

class Info:
    name = "ftp_server"
    author = "ryanq.47"

'''

### Current ftp flow idea

multiple users. 

create a user per assesment, etc or whatever. this creates a dedicated directory for them, then to export on client, just do:
`ftp upload filewhatever user pass`

this will require a user/pass input, or it could just be anonymous uploads? who knows

intentially seperate from creds to log into server, as these accounts are meant to be used as oneoff's or sometihng. 


'''

# assign FTP server to instance
# actually prob, need to do a check if ftp server exists. 

# Optional route example
@app.route('/ftp', methods=['GET'])
def ftp_home():
    return jsonify({"somekey": "somevalue"})

#@jwt_required
@app.route('/ftp/start', methods=['GET'])
def ftp_start_server():
    try:
        instance = Instance()

        ip = Config().config.server.ftp.bind.ip
        port = Config().config.server.ftp.bind.port
        anonymous_user = Config().config.server.ftp.users.anonymous
        banner = Config().config.server.ftp.misc.banner

        # Check if the FTP server has been set or if it is not running
        if instance.ftp_server is None or not instance.ftp_server.running:
            # Initialize and start the FTP server
            instance.ftp_server = LeFTPServer(ip=ip, port=port, banner=banner)
            instance.ftp_server.start_server()

            if anonymous_user:
                logger.info("Adding anonymous FTP user with write-only access")
                instance.ftp_server.add_anonymous_user()
            
            return api_response(
                status=200,
                message=f"FTP server started"
            )

        else:
            return api_response(
                status=400,
                message=f"FTP server is already running"
            )
        
    except Exception as e:
        logger.error(e)

        return api_response(
            status=500
        )

@app.route('/ftp/stop', methods=['GET'])
def ftp_stop_server():
    try:
        instance = Instance()

        if instance.ftp_server is None or not instance.ftp_server.running:
            return api_response(
                status=400,
                message=f"FTP server is not running"
            )

        instance.ftp_server.stop_server()
        return api_response(
            status=200,
            message=f"FTP server stopped successfully"
        )    
    
    except Exception as e:
        logger.error(e)

        return api_response(
            status=500
        )    

@app.route('/ftp/new-user', methods=['POST'])
#@jwt_required()
def ftp_new_user():
    instance = Instance()
    # Get JSON data from request
    data = request.get_json()

    # Retrieve username and password from JSON data
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return api_response(
            status=400,
            message=f"`username` and `password` are required"
        )    

    try:
        #ftp_server = instance.ftp_server
        if instance.ftp_server is None or not instance.ftp_server.running:
            return api_response(
                status=400,
                message=f"FTP server is not running"
            )        
            
        else:
            instance.ftp_server.add_user(
                username = username,
                password = password
            )

            return api_response(
                status=200,
                message=f"User added: {username}"
            )

    except Exception as e:
        logger.error(e)
        return api_response(
            status=500
        )