from flask import current_app
from backend.models import Port, Ship
import requests



def create_ship(home_port):
	cargo = random.randrange(0,10)
	cannon = random.randrange(0,5)
	crew = random.randrange(0,5)
	life_points = random.randrange(0,10)
	ship_id = random.randrange(0,500)

	return Ship(ship_id=ship_id, is_bot=True, cargo=cargo, cannon=cannon, 
		life_points=life_points, crew=crew, home_port=home_port)

def create_port(is_dest, game_id, xcoord=None, ycoord=None):
	cargo = random.randrange(0,30)
	food = random.randrange(0,30)
	x_coord = xcoord
	y_coord = ycoord
	port_id = random.randrange(0,500)

	if not x_coord:
		x_coord = random.randrange(-25,25)
	if not y_coord:
		y_coord = random.randrange(-25,25)


	return Port(port_id=port_id, food=food, x_coord=x_coord, y_coord=y_coord, 
		cargo=cargo, game_id=game_id, is_dest=is_dest)





