from flask import Blueprint, request, current_app
from backend.models import Port
from backend import db, mail
from utils import create_ship, create_port
import db
import json
import requests
from datetime import datetime
from flask_mail import Message

events = Blueprint('queues', __name__)


# Checker to see whether or not is the server running
@events.route('/event', methods=['GET'])
def checker():
    return "Hello"

"""
Generates a game with the game info
"""
@events.route('/generate', methods=['GET','POST'])
def generate():
	playerData = request.get_json()
	game_id = playerData["gameId"]
	dests = [create_port(is_dest=True, game_id=game_id) for i in range(30)]
	ports = [create_port(is_dest=False, game_id=game_id) for i in range(9)]
	ships = []
	for dest in dests:
		num = random.randange(0,3)
		if num % 2 == 0:
			ships.append(create_ship(dest.port_id))

	for dest in dests:
		db.session.add(dest)

	for port in ports:
		db.session.add(port)

	for ship in ships:
		db.session.add(ship)

	db.session.commit()
	return True





