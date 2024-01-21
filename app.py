"""Module to contain and run the endpoints for the Deloton staff API"""

from datetime import datetime
from flask import Flask, current_app, render_template, request
from jinja2 import Template, Environment, FileSystemLoader

import backend

app = Flask(__name__, template_folder='templates')
app.json.sort_keys = False



@app.route("/", methods=["GET"])
def display_game():
    """ Creates an index route with an index page for the API """
    print(game.board)
    return render_template('game.html', counters = game.board, finished_tokens = game.finished_tokens, die_number = game.players[0].die_roll, player_turn = game.players[0].colour)


@app.route("/move_piece", methods = ["POST"])
def move_piece():
    print(request.form['colour'], request.form['square_num'])
    game.move_piece(int(request.form['square_num']), request.form['colour'])
    return display_game()


@app.route("/roll_die", methods=["POST"])
def roll_die():
    game.players[0].roll_die()
    print(game.players[0].die_roll)
    return display_game()

if __name__ == "__main__":
    game = backend.Game(2)
    for colour in ['red', 'green', 'blue']:
        game.add_player(backend.Player(colour))

    print(game.board)

    app.run(debug=True, host="0.0.0.0", port=5000)
