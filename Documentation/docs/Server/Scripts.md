# Scripts

There's some bash scripts provided to make developemnt a bit easier. 

Most of these scripts are in `development/scripts/`, however there's a few floating around in other places

## create_plugin.sh
Creates a barebones plugin in the current directory. You can then copy this to the plugins directory (`app/plugins`) for it to be included on startup.

## prep_for_release.sh
Goes through the project, and removes the following files:
*.db
*.env
*.log

located in root of project

## run_tests.sh
Clears the DB, starts the server, and runs the code tests in the `development/tests/` directory. Meant to imitate a fresh install to test everything. 

Does *not* create a new `.env` file, instead it uses the prexisting one. 