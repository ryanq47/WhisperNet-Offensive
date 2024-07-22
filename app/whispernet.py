from flask import Flask


if __name__ == "__main__":
    try:
        whispernet = Flask(__name__)
        whispernet.run(debug=True)
    except Exception as e:
        print(e)
