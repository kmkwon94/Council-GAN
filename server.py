from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, after_this_request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from after_response import AfterResponse, AfterResponseMiddleware
app = Flask("after_response")
app.config['JSON_AS_ASCII'] = False
AfterResponse(app)
CORS(app)

@app.route("/")
def render_file():
    return "hi", 201
    
    @app.after_response
    def say_hi():
        print("say hi")

@app.route("/test")
def test():
    return "test", 201

@app.after_response
def say_test():
    print("say test hi")

@app.after_response
def say_test2():
    print("say test2 hi yo!")
if __name__ == '__main__':
    # server execute
    app.run(host='0.0.0.0', port=80, debug=True)