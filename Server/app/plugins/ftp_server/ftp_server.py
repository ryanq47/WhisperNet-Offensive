from flask import jsonify, request
from modules.instances import Instance
from modules.log import log
from flask_jwt_extended import jwt_required, get_jwt_identity
from plugins.ftp_server.modules.ftp import LeFTPServer
from threading import Thread
from modules.utils import api_response
from modules.config import Config
import uuid
from modules.redis_models import Plugin
from modules.tls import generate_pem

logger = log(__name__)
app = Instance().app

class Info:
    name = "ftp_server"
    author = "ryanq.47"
    info = "An FTP Server"

'''
### Current FTP Flow Idea

Multiple users. 

Create a user per assessment, etc., or whatever is needed. This creates a dedicated directory for them, then to export on client, just do:
`ftp upload filewhatever user pass`

This will require a user/pass input, or it could just be anonymous uploads. Who knows?

Intentionally separate from creds to log into server, as these accounts are meant to be used as one-offs or something.
'''

# Route to test FTP server setup
#@app.route('/ftp', methods=['GET'])
#def ftp_home():
#    return jsonify({"status": "FTP server route is active"})

## Add to redis and register plugin
try:
    p = Plugin(
        name=Info.name,
        start = "ftp/start",
        stop = "ftp/stop",
        info = Info.info
    )
    p.save()
except Exception as e:
    logger.error(e)

# Check for TLS certificate and key
cert_file = Config().launch_path / Config().config.server.ftp.tls.tls_crt_file
key_file  = Config().launch_path / Config().config.server.ftp.tls.tls_key_file
#path is correct, not writing tho?
#/home/kali/Documents/GitHub/WhisperNet-Offensive/Server/app/modules/plugins/ftp_server/ftp_cert.pem

# Validate if files exist
if not cert_file.exists() or not key_file.exists():
    logger.warning("FTP TLS certificate or key file not found.")

    # If either the certificate or key file is missing, trigger PEM generation.
    # (You'll handle the generate_pem function call with correct paths and filenames)
    logger.info(f"Generating new FTP TLS certificate: {cert_file}")
    logger.info(f"Generating new FTP TLS key: {key_file}")

    # Assuming generate_pem requires paths as inputs, you could call it like this:
    key_path = key_file.parent # parent path
    key_name = key_file.stem # file w/o extenion
    cert_path = cert_file.parent
    cert_name = cert_file.stem
    generate_pem(key_path, key_name, cert_path, cert_name)


# Route to start the FTP server
@app.route('/ftp/start', methods=['POST'])
@jwt_required()  # Uncomment this if JWT protection is needed
def ftp_start_server():
    instance = Instance()
    try:
        # Configuration values
        ip = Config().config.server.ftp.bind.ip
        port = Config().config.server.ftp.bind.port
        anonymous_user = Config().config.server.ftp.users.anonymous.enabled
        banner = Config().config.server.ftp.misc.banner
        sid = uuid.uuid4()

        # Check if the FTP server is not set or not running
        if instance.ftp_server is None or not instance.ftp_server.running:
            instance.ftp_server = LeFTPServer(ip=ip, port=port, banner=banner, sid=sid)
            instance.ftp_server.start_server()

            if anonymous_user:
                logger.info("Adding anonymous FTP user with write-only access")
                instance.ftp_server.add_anonymous_user()
        

            return api_response(status=200, message="FTP server started successfully")
        else:
            return api_response(status=400, message="FTP server is already running")

    except Exception as e:
        import traceback
        logger.error(f"Error starting FTP server: {e}")
        print(traceback.format_exc())  # Log the full traceback

        return api_response(status=500, message="Internal server error")

# Route to stop the FTP server
@app.route('/ftp/stop', methods=['POST'])
@jwt_required()  # Uncomment this if JWT protection is needed
def ftp_stop_server():
    instance = Instance()
    try:
        if instance.ftp_server is None or not instance.ftp_server.running:
            return api_response(status=400, message="FTP server is not running")

        instance.ftp_server.stop_server()
        return api_response(status=200, message="FTP server stopped successfully")

    except Exception as e:
        logger.error(f"Error stopping FTP server: {e}")
        return api_response(status=500, message="Internal server error")

# Route to add a new FTP user
@app.route('/ftp/new-user', methods=['POST'])
@jwt_required()  # Uncomment this if JWT protection is needed
def ftp_new_user():
    instance = Instance()
    data = request.get_json()

    # Validate input data
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return api_response(status=400, message="`username` and `password` are required")

    try:
        if instance.ftp_server is None or not instance.ftp_server.running:
            return api_response(status=400, message="FTP server is not running")

        instance.ftp_server.add_user(username=username, password=password)
        return api_response(status=200, message=f"User added: {username}")

    except Exception as e:
        logger.error(f"Error adding new FTP user: {e}")
        return api_response(status=500, message="Internal server error")
