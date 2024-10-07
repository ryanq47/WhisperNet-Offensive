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

#dep
"""
@app.route('/binary_builder/<target>', methods=['POST'])
def build_target(target):
    try:
        match target:
            case "x64_windows_dropper":
                logger.info("Building target: x64_windows")
                # get config value
                dockerfile_path = Config().config.server.binaries.dropers.x64_windows_dropper
            case _:
                logger.info(f"Unknown target: {target}")
                return api_response(
                    message="Unknown target",
                    code=400
                )

        output_dir      = str((Config().launch_path / "data" / "compiled").absolute())
        build_context   = str(Config().root_project_path) #str((Config().launch_path).absolute() / "..")

        logger.debug(f"Compiled output directory: {output_dir}")
        logger.debug(f"Docker build Context: {build_context}")

        #output_dir = "./data/compiled/" #pathify this

        build(
            dockerfile_path = dockerfile_path,
            output_dir = output_dir,
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
"""
@app.route('/binary_builder/build/custom', methods=['POST'])
def build_custom(target):
    '''
        Build target

        json: 

        {
            "target":"x64_windows_dropper,
            "shellcode":"aabbcc=="
        }

    '''
    try:
        match target:
            case "x64_windows_dropper":
                logger.info("Building target: x64_windows")
                # get config value
                dockerfile_path = Config().config.server.binaries.dropers.x64_windows_dropper
            case _:
                logger.info(f"Unknown target: {target}")
                return api_response(
                    message="Unknown target",
                    code=400
                )

        output_dir      = str((Config().launch_path / "data" / "compiled").absolute())
        build_context   = str(Config().root_project_path) #str((Config().launch_path).absolute() / "..")

        logger.debug(f"Compiled output directory: {output_dir}")
        logger.debug(f"Docker build Context: {build_context}")

        #output_dir = "./data/compiled/" #pathify this

        build(
            dockerfile_path = dockerfile_path,
            output_dir = output_dir,
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

@app.route('/binary_builder/build/dropper', methods=['POST'])
def build_dropper(target):
    '''
        Build target

        json: 

        {
            "target":"x64_windows_dropper,
        }

    '''
    try:
        match target:
            case "x64_windows_dropper":
                logger.info("Building target: x64_windows")
                # get config value
                dockerfile_path = Config().config.server.binaries.dropers.x64_windows_dropper
            case _:
                logger.info(f"Unknown target: {target}")
                return api_response(
                    message="Unknown target",
                    code=400
                )

        output_dir      = str((Config().launch_path / "data" / "compiled").absolute())
        build_context   = str(Config().root_project_path) #str((Config().launch_path).absolute() / "..")

        logger.debug(f"Compiled output directory: {output_dir}")
        logger.debug(f"Docker build Context: {build_context}")

        #output_dir = "./data/compiled/" #pathify this

        build(
            dockerfile_path = dockerfile_path,
            output_dir = output_dir,
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

@app.route('/binary_builder/build/agent', methods=['POST'])
def build_agent(target):
    '''
        Build target

        json: 

        {
            "target":"x64_windows_dropper,
            "type": "dropper",
            "shellcode":"aabbcc=="
        }

    '''
    try:
        match target:
            case "x64_windows_dropper":
                logger.info("Building target: x64_windows")
                # get config value
                dockerfile_path = Config().config.server.binaries.dropers.x64_windows_dropper
            case _:
                logger.info(f"Unknown target: {target}")
                return api_response(
                    message="Unknown target",
                    code=400
                )

        output_dir      = str((Config().launch_path / "data" / "compiled").absolute())
        build_context   = str(Config().root_project_path) #str((Config().launch_path).absolute() / "..")

        logger.debug(f"Compiled output directory: {output_dir}")
        logger.debug(f"Docker build Context: {build_context}")

        #output_dir = "./data/compiled/" #pathify this

        build(
            dockerfile_path = dockerfile_path,
            output_dir = output_dir,
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


@app.route('/binary_builder/targets', methods=['GET'])
def valid_targets():
    '''
        Returns a list of valid compile targets
    '''
    try:

        droppers_dict = {
            key: (value if value else 'No buildfile')
            for key, value in Config().config.server.binaries.droppers.items()
        }

        agents_dict = {
            key: (value if value else 'No buildfile')
            for key, value in Config().config.server.binaries.agents.items()
        }

        customs_dict = {
            key: (value if value else 'No buildfile')
            for key, value in Config().config.server.binaries.customs.items()
        }

        final_response = {
            'droppers': droppers_dict,
            'agents': agents_dict,
            'customs': customs_dict
        }

        ''' Output example: 
            {
            "data": {
                "agents": {
                "x64_windows": "No Dockerfile"
                },
                "droppers": {
                "x64_windows": "_docker/dockerfiles/debian_windows_x64.dockerfile",
                "x86_windows": "No Dockerfile"
                }
            },
            "message": "",
            "rid": "af073584-5af9-4592-9338-0ebc03e49310",
            "status": 200,
            "timestamp": 1728241553
            }
        '''

        return api_response(data=final_response)

    except Exception as e:
        logger.error(e)
        return api_response(
            status=500
        )