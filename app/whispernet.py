from flask import Flask



if __name__ == "__main__":
    whispernet = Flask(__name__)
    whispernet.run(debug=True)