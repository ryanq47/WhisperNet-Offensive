from flask import jsonify
from modules.instances import Instance
from modules.log import log
from modules.config import Config
from modules.docker_builder import build
from modules.utils import api_response

logger = log(__name__)
app = Instance().app

class Info:
    name = "binary_builder"
    author = "ryanq.47"

# Optional route example
@app.route('/binary_builder', methods=['GET'])
def buinary_builder():
    return jsonify({"somekey": "somevalue"})

## routes:
# /binary_builder/<name_of_target?>

# then if tree it for names based on supported items?
# not super modular but it works  


@app.route('/binary_builder/<target>', methods=['POST'])
def build_target(target):
    try:
        match target:
            case "x64_windows_dropper":
                logger.info("Building target: x64_windows")
                # get config value
                dockerfile_path = Config().config.server.docker.buildfiles.droppers.x64_windows
                # code for pattern 1
            #case pattern2:
                # code for pattern 2

            case _:
                logger.info(f"Unknown target: {target}")
                return api_response(
                    message="Unknown target",
                    code=400
                )

        # [X] pathify
        # move this to the data/output
        output_dir      = str((Config().launch_path / "data" / "compiled").absolute())
        build_context   = str(Config().root_project_path) #str((Config().launch_path).absolute() / "..")

        logger.debug(f"Compiled output directory: {output_dir}")
        logger.debug(f"Docker build Context: {build_context}")

        #output_dir = "./data/compiled/" #pathify this

        build(
            dockerfile_path = dockerfile_path,
            output_dir = output_dir,
            #build_context = "../" # moving this up one dir. Should prolly use base path here instead of this ../
            build_context = build_context
        )

        return api_response(
            message=f"successfully built {target}",
            status=200
        )
    except Exception as e:
        logger.error(e)
        return api_response(
            message="An error occured",
            status=500
        )       