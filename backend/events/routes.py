from flask import Blueprint, request, current_app
from backend import db, mail
import json
import requests
from datetime import datetime
from flask_mail import Message

events = Blueprint('queues', __name__)


# Checker to see whether or not is the server running
@events.route('/event', methods=['GET'])
def checker():
    return "Hello"
