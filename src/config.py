import os
import secrets

from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from dotenv import load_dotenv

## charge enviroment variables
load_dotenv()

app = Flask(__name__)

# Swagger config
template = {
    "swagger": "2.0",
    "info": {
        "title": "Validate Email APIs",
        "description": "Microservice to validate emails",
        "contact": {
            "responsibleOrganization": "Unknown",
            "responsibleDeveloper": "Deiver Vasquez",
            "email": "estudiandovazmore@gmail.com",
        },
        "version": "0.1.0"
    },
}

swagger = Swagger(app, template=template)

app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")

tokens_session = secrets.token_hex(20)
app.config["SECRET_KEY"] = tokens_session

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
