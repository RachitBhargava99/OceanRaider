from flask import current_app
from backend.models import Port, Ship
import requests
import random
import math


def create_ship(home_port, ship_id, game_id, cannon=None):
    cargo = random.randrange(0, 10)
    cannon = random.randrange(0, 5) if cannon is None else cannon
    crew = random.randrange(1, 5)
    life_points = random.randrange(5, 10)
    ship_id = ship_id

    return Ship(ship_id=ship_id, is_bot=True, cargo=cargo, cannon=cannon, life_points=life_points, crew=crew,
                home_port=home_port, curr_port=home_port, game_id=game_id)


def create_port(is_dest, game_id, x_coord=None, y_coord=None):
    cargo = random.randrange(0, 30)
    food = random.randrange(0, 30)
    port_id = random.randrange(0, 500)

    if not x_coord:
        x_coord = random.randrange(-25, 25)
    if not y_coord:
        y_coord = random.randrange(-25, 25)

    return Port(port_id=port_id, food=food, x_coord=x_coord, y_coord=y_coord, cargo=cargo, game_id=game_id,
                is_dest=is_dest)


def price_calc(trade_type, ship, barg):
    base_exchange = {
        'life': 1,
        'cargo': 2,
        'cannon': 5,
        'crew': 10,
        'food': 0.5,
        'speed': 25
    }

    base = 0.5 if not ship.home_port else 1
    prohibited_barg_sell = ['speed', 'life']

    if barg not in base_exchange:
        return {'status': 2, 'error': "Unknown Exchange Requested"}
    if trade_type == 'SELL' and barg in prohibited_barg_sell:
        return {'status': 2, 'error': "Prohibited Exchange Attempt Detected"}
    if trade_type != 'BUY' and trade_type != 'SELL':
        return {'status': 2, 'error': "Unknown Trade Requested"}

    if trade_type == 'SELL':
        base *= 0.75 if not ship.home_port else 0.8

    exchange_rate = base_exchange[barg] * base

    return {'status': 0, 'exchange_rate': exchange_rate}


def show_buy_sell_prices(ship):
    buyables = ['life', 'cargo', 'cannon', 'crew', 'food', 'speed']
    sellables = ['cargo', 'cannon', 'crew', 'food']
    price_dict = {
        'BUY': {curr_buy: price_calc('BUY', ship, curr_buy) for curr_buy in buyables},
        'SELL': {curr_sell: price_calc('SELL', ship, curr_sell) for curr_sell in sellables}
    }
    return price_dict


def euclidean_dist(coor_1, coor_2):
    return math.sqrt((coor_1[0] - coor_2[0]) ** 2 + (coor_1[1] - coor_2[1]) ** 2)


def travel_cost(ship, dest_port_id):
    curr_port = Port.query.filter_by(id=ship.home_port).first()
    dest_port = Port.query.filter_by(id=dest_port_id).first()
    distance = euclidean_dist((curr_port.x_coord, curr_port.y_coord), (dest_port.x_coord, dest_port.y_coord))
    food_cost = math.floor(distance * 0.5)
    cargo_cost = math.floor(distance * 0.2)
    return [food_cost, cargo_cost]
