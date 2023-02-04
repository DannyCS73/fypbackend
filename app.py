from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, request, jsonify, make_response, abort
from flask_migrate import Migrate

application = Flask(__name__)
application.config['SECRET_KEY'] = 'uhfyidhbj'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartoffice.db'
CORS(application)

db = SQLAlchemy(application)
migrate = Migrate(application,db)
