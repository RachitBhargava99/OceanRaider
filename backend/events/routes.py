from flask import Blueprint, request, current_app, flash, redirect, url_for, render_template
from backend.models import Port, Game, Ship
from flask_login import current_user
from backend import db, mail
from backend.events.utils import create_ship, create_port, travel_cost, show_buy_sell_prices, price_calc
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
        return redirect(url_for('events.show_games'))

    else:
        flash("You must be logged in to proceed.", 'danger')
        return redirect(url_for('users.login'))


@events.route('/games', methods=['GET'])
def show_games():
    if current_user.is_authenticated:
        user_id = current_user.user_id
        all_player_games = Game.query.filter_by(user_id=user_id)
        game_ids = [game.id for game in all_player_games]
        return render_template('gamepage.html', ids=game_ids)

    else:
        flash("You must be logged in to proceed.", 'danger')
        return redirect(url_for('users.login'))


@events.route('/loadgame/<int:game_id>', methods=['GET'])
def load_game(game_id):
    if current_user.is_authenticated:
        if Game.query.filter_by(id=game_id).first().user_id == current_user.user_id:
            current_user.game_id = game_id
            db.session.commit()
            return redirect(url_for('events.show_map'))
        else:
            flash("You are not the player in the requested game.", 'danger')
            return redirect(url_for('show_games'))
    else:
        flash("You must be logged in to proceed.", 'danger')
        return redirect(url_for('users.login'))


@events.route('/travel/<int:port_id>', methods=['GET'])
def travel_port(port_id):
    if current_user.is_authenticated:
        game_id = current_user.game_id
        player_ship = Ship.query.filter_by(game_id=game_id, is_bot=False).first()
        food_cost, cargo_cost = travel_cost(player_ship.curr_port, port_id)
        if food_cost > player_ship.food and cargo_cost > player_ship.cargo:
            player_ship.curr_port = port_id
            player_ship.food -= food_cost
            player_ship.cargo -= cargo_cost
            db.session.commit()
        else:
            flash("Insufficient Resources Available for this travel", 'danger')
        return redirect(url_for('events.show_map'))
    else:
        flash("You must be logged in to proceed.", 'danger')
        return redirect(url_for('users.login'))


@events.route('/market', methods=['GET'])
def show_market_prices():
    if current_user.is_authenticated:
        game_id = current_user.game_id
        player_ship = Ship.query.filter_by(game_id=game_id, is_bot=False).first()
        all_prices = show_buy_sell_prices(player_ship)
        return render_template('market.html', prices=all_prices, player_ship=player_ship)
    else:
        flash("You must be logged in to proceed.", 'danger')
        return redirect(url_for('users.login'))


@events.route('/trade/<string:trade_type>/<string:item>/<int:num>')
def trade(trade_type, item, num):
    if current_user.is_authenticated:
        game_id = current_user.game_id
        player_ship = Ship.query.filter_by(game_id=game_id, is_bot=False).first()
        price_dict = price_calc(trade_type, player_ship, item)
        if price_dict['status'] == 2:
            flash(price_dict['error'], 'danger')
            return redirect(url_for('events.show_market_prices'))
        base_exchange = price_dict['exchange_rate']
        total_cost = base_exchange * num
        if trade_type == 'BUY':
            if player_ship.coin < total_cost:
                flash("You do not have enough money for this purchase.", 'danger')
                return redirect(url_for('events.show_market_prices'))
            exec(f"player_ship.{item} += {num}")
            player_ship.coin -= total_cost
        else:
            exec(f"if player_ship.{item} < num: flash(\"You do not have enough items to sell.\", 'danger')" +
                 f" and return redirect(url_for('events.show_market_prices'))")
            exec(f"player_ship.{item} -= num")
            player_ship.coin += total_cost
        flash("Trade Successful")
        return redirect(url_for('events.show_market_prices'))
