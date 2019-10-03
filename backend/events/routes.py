from flask import Blueprint, request, current_app, flash, redirect, url_for, render_template
from backend.models import Port, Game
from flask_login import current_user
from backend import db, mail
from backend.events.utils import create_ship, create_port
import random
import json
import requests
from datetime import datetime
from flask_mail import Message

events = Blueprint('events', __name__)


# Checker to see whether or not is the server running
@events.route('/event', methods=['GET'])
def checker():
    return "Hello"


"""
Generates a game with the game info
"""
@events.route('/generate', methods=['GET'])
def generate():
    if current_user.is_authenticated:
        user_id = current_user.user_id
        new_game = Game(user_id=user_id)
        db.session.add(new_game)
        db.session.commit()
        game_id = new_game.id
        print(game_id)
        dests = [create_port(is_dest=True, game_id=game_id) for i in range(30)]
        ports = [create_port(is_dest=False, game_id=game_id) for i in range(9)]
        ships = []
        num_ships = 0

        for dest in dests:
            num = random.randrange(0, 3)
            if num % 2 == 0:
                ships.append(create_ship(dest.port_id, num_ships, game_id))
                num_ships += 1

        [db.session.add(obj) for obj in (dests + ports + ships)]

        db.session.commit()
        return redirect(url_for('events.checker'))

    else:
        flash("You must be logged in to proceed.", 'danger')
        return redirect(url_for('users.login'))

@events.route('/loadgame', methods=['GET'])
def load_game(game_id):
    game = Game.query.filter_by(id=game_id)
    

@events.route('/gamepage', methods=['GET'])
def show_game():
    return render_template("gamepage.html")









