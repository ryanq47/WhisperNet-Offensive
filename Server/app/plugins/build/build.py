import json
import signal
import socket
import struct
from multiprocessing import Process

from flask import request, send_from_directory
from flask_jwt_extended import jwt_required  # if you need JWT
from flask_restx import Namespace, Resource, fields

from modules.agent import BaseAgent
from modules.instances import Instance
from modules.listener import BaseListener
from modules.log import log
from plugins.build.modules.build_interface import HttpBuildInterface
import hashlib
from modules.config import Config
import pathlib
import os

# from modules.redis_models import ActiveService
from modules.utils import api_response

# ------------------------------------------------------------------------------------
#   Docs
# ------------------------------------------------------------------------------------
"""
# Pre Docs:


"""

logger = log(__name__)
app = Instance().app


class Info:
    name = "build"
    author = "ryanq.47"


# ------------------------------------------------------------------------------------
#   1) Create a dedicated Namespace for the Beacon HTTP plugin
# ------------------------------------------------------------------------------------
build_ns = Namespace(
    "Plugin: build",
    description="Build plugin for agents",
)

# ------------------------------------------------------------------------------------
#   2) Define a standard response model (similar to stats_response in your example)
# ------------------------------------------------------------------------------------
build_response = build_ns.model(
    "BuildResponse",
    {
        "rid": fields.String(description="Request ID"),
        "timestamp": fields.String(description="Request Timestamp, Unix Time"),
        "status": fields.Integer(description="Response Code", default=200),
        "data": fields.Raw(description="Data from server response"),
        "message": fields.String(description="Message or status info"),
    },
)

# ------------------------------------------------------------------------------------
#   3) Define Resource classes + routes
# ------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------
#   List compiled agents/exe's/etc
# ------------------------------------------------------------------------------------


def compute_file_md5(file_path):
    hash_md5 = hashlib.md5()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@build_ns.route("/compiled")
class StaticServeListFilesResource(Resource):
    """
    GET /plugin/static-serve/list_files
    Returns a JSON list of all files currently stored in the static directory,
    each with filename, filehash, and a webserver path (/static/filename).
    """

    @build_ns.marshal_with(build_response, code=200)
    @jwt_required()
    def get(self):
        logger.warning("UNAUTH, /build/files")

        # Example path: 'data/static' (adjust as needed)
        static_dir = pathlib.Path(Config().root_project_path) / "data" / "compiled"

        if not static_dir.exists():
            return api_response(
                data=[], message="No static directory found. No files are being served."
            )

        file_info_list = []
        for item in static_dir.iterdir():
            if item.is_file():
                # Compute file hash on the fly
                file_hash = compute_file_md5(item)
                # Build a dictionary for each file
                file_info_list.append(
                    {
                        "filename": item.name,
                        "filehash": file_hash,
                        "filepath": f"/build/{item.name}",  # Webserver path
                    }
                )

        return api_response(
            data=file_info_list, message="List of files in static directory."
        )


@build_ns.route("/upload")
class BuildUploadResource(Resource):
    """
    POST /plugin/static-serve/upload
    Allows an operator to upload a file to the server's static directory.
    """

    @build_ns.doc(
        responses={200: "Success", 400: "Bad Request", 500: "Server Error"},
        description="Upload a file to the static serving directory",
    )
    @jwt_required()
    def post(self):
        # file = request.files["file"]
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return api_response(message="No file provided"), 400

        if not uploaded_file:
            return api_response(status=400, data=None, message="No file provided")

        # Determine the final filename
        original_filename = uploaded_file.filename
        final_filename = original_filename  # The thought was to maybe have the user be able to change the file name, but that's too much work rn. is a nice to have, don't need rn.
        # = requested_name if requested_name else original_filename

        # Build absolute path to static folder
        static_dir = os.path.join(Config().root_project_path, "data/compiled/")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, exist_ok=True)

        # Potentially sanitize or randomize name if needed
        # For example: final_filename = str(uuid.uuid4()) + "_" + final_filename
        file_path = os.path.join(static_dir, final_filename)

        # Save file
        try:
            uploaded_file.save(file_path)
            logger.debug(f"Saved uploaded file successfully at {file_path}")
        except Exception as e:
            logger.exception("Failed to save uploaded file.")
            return api_response(status=500, data=None, message=str(e))

        # Construct public URL (assuming Flask serves static from "/static")
        # If your Flask app is serving static at a different route, adjust accordingly.
        public_url = f"/compiled/{final_filename}"

        return api_response(
            status=200, data={"url": public_url}, message="File uploaded successfully"
        )


# ------------------------------------------------------------------------------------
#   Build
# ------------------------------------------------------------------------------------


@build_ns.route("/<string:agent_type>/build")
class BeaconHttpListenerSpawnResource(Resource):
    """
    POST /plugin/beacon-http/listener/spawn
    """

    @build_ns.marshal_with(build_response, code=200)
    @jwt_required()
    def post(self, agent_type):
        """Post a new build job"""
        logger.debug("UNAUTH ENPDOINT /<string:agent_type>/build")

        data = request.get_json() or {}
        callback_port = data.get("callback_port")
        callback_address = data.get("callback_address")
        agent_name = data.get("agent_name")
        agent_type = data.get("agent_type")
        build_script = data.get("build_script")

        build_job = HttpBuildInterface(
            agent_type=agent_type,
            agent_name=agent_name,
            callback_address=callback_address,
            callback_port=callback_port,
            build_script=build_script,
        )

        build_id = build_job.build()

        build_response_dict = {
            "build_id": build_id,
        }

        return api_response(data=build_response_dict)


# ------------------------------------------------------------------------------------
# List available agents scripts
# ------------------------------------------------------------------------------------
@build_ns.route("/<string:agent_type>/scripts")
class BuildGetAgentTemplatesResource(Resource):
    """
    GET /agent-templates/<string:agent_type>/scripts

    get list of build scripts for an agent.

    """

    # @build_ns.marshal_with(build_response, code=200)
    @jwt_required()
    def get(self, agent_type):
        # compiled_dir = pathlib.Path(Config().root_project_path) / "data" / "compiled"
        # return send_from_directory(compiled_dir, filename)

        agent_script_dir = (
            pathlib.Path(Config().root_project_path)
            / "data"
            / "agent_templates"
            / agent_type
            / "scripts"
        )

        logger.debug(agent_script_dir)

        # injection check. - only use for .resolve()
        # if not agent_script_dir.is_relative_to(
        #     pathlib.Path(Config().root_project_path)
        # ):  # Python 3.9+
        #     # raise ValueError("Invalid path")
        #     logger.warning(f"Invalid path detected: '{agent_script_dir}'")
        #     return api_response(), 500

        # get only directories, which show which agent templates are available
        scripts = [
            item.name for item in agent_script_dir.iterdir() if item.suffix == ".py"
        ]

        return api_response(data=scripts)


# ------------------------------------------------------------------------------------
# Simple Serve Resource
# ------------------------------------------------------------------------------------
@build_ns.route("/<path:filename>")
class BuildServeResource(Resource):
    """
    GET /<filename>
    Serve any file in data/compiled.

    """

    logger.debug("UNAUTH ENPDOINT /build/file*")

    # @jwt_required()
    def get(self, filename):
        # can't use headers iwth ui.downlaod, so this has to be unauth for now -_-
        logger.warning(
            "UNAUTH: /build/*, aka generated payloads. Issue w nicegui, ui.download, and no headers"
        )
        compiled_dir = pathlib.Path(Config().root_project_path) / "data" / "compiled"
        return send_from_directory(compiled_dir, filename)


# ------------------------------------------------------------------------------------
# List of build scripts for that agent
# ------------------------------------------------------------------------------------
@build_ns.route("/agent-templates/")
class BuildGetAgentTemplatesResource(Resource):
    """
    GET /agent-templates

    get list of agent templates

    """

    # @build_ns.marshal_with(build_response, code=200)
    @jwt_required()
    def get(self):
        # compiled_dir = pathlib.Path(Config().root_project_path) / "data" / "compiled"
        # return send_from_directory(compiled_dir, filename)

        agent_template_dir = (
            pathlib.Path(Config().root_project_path) / "data" / "agent_templates"
        )

        # get only directories, which show which agent templates are available
        directories = [
            item.name for item in agent_template_dir.iterdir() if item.is_dir()
        ]

        return api_response(data=directories)


# ------------------------------------------------------------------------------------
# Simple delete Resource
# ------------------------------------------------------------------------------------


@build_ns.route("/delete/<path:filename>")
class StaticServeDeleteFileResource(Resource):
    """
    DELETE /static-serve/delete/<filename>
    Deletes the specified file from data/static.
    """

    # @jwt_required  # uncomment if you want JWT protection
    @build_ns.marshal_with(build_response, code=200)
    @jwt_required()
    def delete(self, filename):
        logger.warning("UNAUTH, /DELETE/FILENAME")

        # Build full path to the file using Path
        static_dir = pathlib.Path(Config().root_project_path) / "data" / "compiled"
        file_path = static_dir / filename

        # Optional: sanitize 'filename' to avoid path traversal attacks
        file_path = static_dir / pathlib.Path(filename).name

        if not file_path.exists():
            return api_response(data=None, message="File not found."), 404

        if not file_path.is_file():
            return api_response(data=None, message="Requested path is not a file."), 400

        try:
            file_path.unlink()  # equivalent to os.remove()
            logger.debug(f"Deleted file: {file_path}")
            return (
                api_response(
                    data=None,
                    message=f"File '{filename}' removed successfully.",
                ),
                200,
            )

        except Exception as e:
            logger.exception("Failed to delete file.")
            return api_response(data=None, message=str(e)), 500


# ------------------------------------------------------------------------------------
#   4) Register the namespace with your Flask-RESTX Api
#      This is typically done once in your initialization code.
# ------------------------------------------------------------------------------------
Instance().api.add_namespace(build_ns, path="/build")
