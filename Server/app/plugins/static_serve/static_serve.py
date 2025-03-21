import os
import uuid

from flask import request, send_from_directory
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from flask_jwt_extended import jwt_required
from modules.instances import Instance
from modules.log import log
from modules.utils import api_response
from modules.config import Config
import hashlib
import pathlib
from werkzeug.utils import secure_filename

logger = log(__name__)

## Note, serving should be safe due to flasks serve from directory

# ALSO - Move me to pathlib


# ------------------------------------------------------------------------------------
# Plugin Info
# ------------------------------------------------------------------------------------
class Info:
    name = "static_serve"
    author = "YourName"


# ------------------------------------------------------------------------------------
# Create the RESTX Namespace
# ------------------------------------------------------------------------------------
static_serve_ns = Namespace(
    "Plugin: static-serve",
    description="Endpoints for quick-and-easy static file serving.",
)
static_serve_file_ns = Namespace(
    "Plugin: static-serve",
    description="NS for specifically serving from / or anywhere in filepath",
)


# ------------------------------------------------------------------------------------
# Define a Response Model (Optional)
# ------------------------------------------------------------------------------------
static_serve_response = static_serve_ns.model(
    "StaticServeResponse",
    {
        "timestamp": fields.String(description="Server-side time of the response"),
        "status": fields.Integer(description="HTTP status code", default=200),
        "data": fields.Raw(description="Generic data field"),
        "message": fields.String(description="Message or status info"),
    },
)

# ------------------------------------------------------------------------------------
# Upload File Resource
# ------------------------------------------------------------------------------------
upload_parser = static_serve_ns.parser()
upload_parser.add_argument(
    "file",
    location="files",
    type=FileStorage,
    required=True,
    help="The file to be uploaded.",
)
upload_parser.add_argument(
    "filename",
    location="form",
    type=str,
    required=False,
    help="Optional new filename. If omitted, uses the original filename.",
)


@static_serve_ns.route("/upload")
class StaticServeUploadResource(Resource):
    """
    POST /plugin/static-serve/upload
    Allows an operator to upload a file to the server's static directory.
    """

    @static_serve_ns.doc(
        responses={200: "Success", 400: "Bad Request", 500: "Server Error"},
        description="Upload a file to the static serving directory",
        parser=upload_parser,
    )
    # @jwt_required
    @static_serve_ns.marshal_with(static_serve_response, code=200)
    @jwt_required()
    def post(self):
        logger.warning("UNAUTH, /upload")
        logger.info("LATER GOAL: Allow structured file upload (aka, in folders)")
        # file = request.files["file"]
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return api_response(message="No file provided"), 400

        if not uploaded_file:
            return api_response(status=400, data=None, message="No file provided")

        # Determine the final filename
        original_filename = secure_filename(uploaded_file.filename)
        final_filename = original_filename  # The thought was to maybe have the user be able to change the file name, but that's too much work rn. is a nice to have, don't need rn.
        # = requested_name if requested_name else original_filename

        # Build absolute path to static folder
        static_dir = os.path.join(Config().root_project_path, "data/static/")
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
        public_url = f"/{final_filename}"

        return api_response(
            status=200, data={"url": public_url}, message="File uploaded successfully"
        )


# ------------------------------------------------------------------------------------
# Delete File
# ------------------------------------------------------------------------------------
@static_serve_ns.route("/delete/<path:filename>")
class StaticServeDeleteFileResource(Resource):
    """
    DELETE /static-serve/delete/<filename>
    Deletes the specified file from data/static.
    """

    # @jwt_required  # uncomment if you want JWT protection
    @static_serve_ns.marshal_with(static_serve_response, code=200)
    @jwt_required()
    def delete(self, filename):
        logger.warning("UNAUTH, /DELETE/FILENAME")
        # Build full path to the file
        static_dir = os.path.join(Config().root_project_path, "data/static")
        file_path = os.path.join(static_dir, filename)

        # Optional: sanitize 'filename' if you don't trust input (avoid path traversal)
        # e.g. file_path = os.path.join(static_dir, os.path.basename(filename))

        if not os.path.exists(file_path):
            return api_response(data=None, message="File not found."), 404

        if not os.path.isfile(file_path):
            return api_response(data=None, message="Requested path is not a file."), 400

        try:
            os.remove(file_path)
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
# Simple Serve Resource (Optional)
# ------------------------------------------------------------------------------------
@static_serve_file_ns.route("/<path:filename>")
class StaticServeFileResource(Resource):
    """
    GET /<filename>
    Serve any file in data/static.

    """

    def get(self, filename):
        static_dir = os.path.join(Config().root_project_path, "data/static/")
        return send_from_directory(static_dir, filename)


# ------------------------------------------------------------------------------------
# Simple Ping/Health Resource (Optional)
# ------------------------------------------------------------------------------------
# @static_serve_ns.route("")
# @static_serve_ns.doc(description="A simple health-check or ping endpoint.")
# class StaticServePingResource(Resource):
#     def get(self):
#         return api_response(data="StaticServe plugin is alive.")


# ------------------------------------------------------------------------------------
# 4) List All Files Being Served
# ------------------------------------------------------------------------------------
def compute_file_md5(filepath, block_size=65536):
    """Compute the MD5 hash of a file, reading in chunks."""
    md5 = hashlib.md5()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            md5.update(chunk)
    return md5.hexdigest()


@static_serve_ns.route("/files")
class StaticServeListFilesResource(Resource):
    """
    List all files that are beingstaticlaly served
    """

    @static_serve_ns.marshal_with(static_serve_response, code=200)
    @jwt_required()
    def get(self):
        logger.warning("UNAUTH, /files")

        # Example path: 'data/static' (adjust as needed)
        static_dir = pathlib.Path(Config().root_project_path) / "data/static"

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
                        "filepath": f"/{item.name}",  # Webserver path
                    }
                )

        return api_response(
            data=file_info_list, message="List of files in static directory."
        )


# ------------------------------------------------------------------------------------
# Register the Namespace
# ------------------------------------------------------------------------------------
# In your main initialization code or wherever you register plugins:
Instance().api.add_namespace(static_serve_ns, path="/static-serve")
Instance().api.add_namespace(static_serve_file_ns, path="/")
