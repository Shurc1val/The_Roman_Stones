"""Module to contain and run the endpoints for the Deloton staff API"""

from math import ceil, sqrt
from os import environ
from random import randint
from time import sleep

from dotenv import load_dotenv
from flask import (Flask, render_template, request, Response, redirect, url_for)
from flask_login import (LoginManager, login_user, current_user, login_required)
from turbo_flask import Turbo

import backend


class User():
    """Class for users for use by flask_login library."""

    def __init__(self, users: list) -> None:
        user_ids = [int(user.get_id()) for user in users]
        self._user_id = self.get_new_user_id(user_ids)
        self._authenticated = False

    def get_id(self):
        """Returns id of user."""
        return self._user_id

    @property
    def is_active(self):
        """Returns if the user is active."""
        return True

    @property
    def is_authenticated(self):
        """Returns if the user is authenticated."""
        return self._authenticated

    @property
    def is_anonymous(self):
        """Returns if the user is anonymous."""
        return False

    @staticmethod
    def get_new_user_id(user_ids: list[int]) -> int:
        """Gets a unique user id."""
        user_id = randint(1, 100000)
        while user_id in user_ids:
            user_id = randint(1, 100000)

        return str(user_id)

    def authenticate_user(self):
        """Sets user _authenticate attribute to true."""
        self._authenticated = True

    def unauthenticate_user(self):
        """Sets user _authenticate attribute to false."""
        self._authenticated = False

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.json.sort_keys = False
app.secret_key = environ['SECRET_KEY']

login_manager = LoginManager()
login_manager.init_app(app)
users = []

turbo = Turbo(app)

COLOURS_AVAILABLE = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo',
                     'violet', 'teal', 'maroon', 'black']


@turbo.user_id
def get_user_id():
    """Gets the id of current user."""
    return current_user.get_id()


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """Gets the User object with user_id matching that given from users list."""
    matches = [user for user in users if user.get_id() == user_id]
    if len(matches) == 0:
        return None

    return matches[0]


@app.route("/login", methods=["GET", "POST"])
def login():
    """Function to make new players login."""
    if request.method == "GET":
        player_colours = [player.colour for player in game.players]
        #player_colours = ['red']
        available_colours_remaining = list(set(COLOURS_AVAILABLE).difference(set(player_colours)))

        user_id = current_user.get_id()

        if not user_id:
            user = User(users)
            if login_user(user):
                users.append(user)
        else:
            user = load_user(user_id)
            if user_id in game.player_ids:
                return redirect(url_for('display_game'))

        if (len(game.players) < game.number_of_players) or game.number_of_players == 0:
            message = {
                'players': player_colours,
                'colours_available': available_colours_remaining}
        else:
            message = {
                'title': "Game Full",
                'text': "Sorry, there are no spots left in this game; feel free to watch."
                }
            return render_template('TRS.html',
                                   counters = game.board,
                                   counters_per_square = max(ceil(sqrt(game.total_number_of_counters)), 3),
                                   finished_tokens = game.finished_tokens,
                                   die_number = game.players[0].die_roll,
                                   player_turn = game.players[0].colour,
                                   message=message)

        return render_template('TRS.html',
                               counters = game.board,
                               counters_per_square = max(ceil(sqrt(game.total_number_of_counters)), 3),
                               finished_tokens = game.finished_tokens,
                               die_number = 0,
                               player_turn = "",
                               message=message)

    elif request.method == "POST":
        user_id = current_user.get_id()

        if user_id in game.player_ids:
            redirect(url_for('display_game'), code=302)

        num_players = request.form.get('num_players')
        counters_per_player = request.form.get('counters_per_player')
        colour = request.form.get('colour').lower()

        if num_players and counters_per_player:
            game.set_num_players_and_counters(int(num_players), int(counters_per_player))

        game.add_player(backend.Player(colour, user_id))
        load_user(user_id).authenticate_user()

        turbo.push(
            turbo.update(
                render_template(
                    'head.html',
                    counters_per_square = max(ceil(sqrt(game.total_number_of_counters)), 3)
                ),
                'head'
            )
        )

        if len(game.players) < game.number_of_players:
            non_player_ids = list(set([user.get_id() for user in users]).difference(set(game.player_ids)))
            player_colours = [player.colour for player in game.players]
            available_colours_remaining = list(set(COLOURS_AVAILABLE).difference(set(player_colours)))
            if non_player_ids:
                turbo.push(
                    turbo.replace(
                        render_template(
                            'game.html',
                            counters = game.board,
                            finished_tokens = game.finished_tokens,
                            die_number = 0,
                            player_turn = "",
                            message={
                                'players': player_colours,
                                'colours_available': available_colours_remaining
                            }
                        ),
                        'game'
                    ),
                    to=non_player_ids
                )

            turbo.push(
                turbo.replace(
                    render_template(
                        'game.html',
                        counters = game.board,
                        finished_tokens = game.finished_tokens,
                        die_number = 0,
                        player_turn = "",
                        message={
                            'title': "Please Wait",
                            'text': f"Please wait for the rest of the players to join ({len(game.players)}/{game.number_of_players})."
                        }
                    ),
                    'game'
                ),
                to=game.player_ids
            )
        else:
            turbo.push(
                turbo.replace(
                    render_template(
                        'game.html',
                        counters = game.board,
                        finished_tokens = game.finished_tokens,
                        die_number = game.players[0].die_roll,
                        player_turn = game.players[0].colour, message={}
                    ),
                    'game'
                )
            )

        return redirect(url_for('display_game'))


@login_manager.unauthorized_handler
def unauthorised():
    """Handler for new users coming to the game; forwards to login page."""
    return redirect(url_for('login'))


@app.route("/", methods=["GET"])
@login_required
def display_game():
    """ Creates an index route with an index page for the API """
    message = {}
    user_id = current_user.get_id()
    if (len(game.players) < game.number_of_players) or len(game.players) == 0:
        if user_id not in game.player_ids:
            return redirect(url_for('login'))
        else:
            message = {
                'title': "Please Wait",
                'text': f"Please wait for the rest of the players to join ({len(game.players)}/{game.number_of_players})."
            }

    return render_template(
        'TRS.html',
        counters = game.board,
        counters_per_square = max(ceil(sqrt(game.total_number_of_counters)), 3),
        finished_tokens = game.finished_tokens,
        die_number = game.players[0].die_roll,
        player_turn = game.players[0].colour,
        message=message
    )


@app.route("/move_piece", methods = ["POST"])
@login_required
def move_piece():
    """Function called to move a selected piece."""
    colour = game.players[0].colour
    game.move_piece(
        int(request.form['square_num']),
        request.form['colour'],
        current_user.get_id()
    )

    turbo.push([
        turbo.replace(
            render_template(
                'board.html',
                counters=game.board,
                counters_per_square = ceil(sqrt(game.total_number_of_counters))
            ),
            'board'
        ),
        turbo.replace(
            render_template(
                'player_turn_label.html',
                player_turn = game.players[0].colour
            ),
            'player_turn_label'
        ),
        turbo.replace(
            render_template(
                'off_board.html',
                finished_tokens=game.finished_tokens
            ),
            'off_board'
        )
    ])

    if game.check_win(colour):
        turbo.push(
            turbo.replace(
                render_template(
                    'popup.html',
                    message={
                        'title': "Winner",
                        'text': f"Congratulations {colour} player, you have won!"
                    }
                ),
                'popup_box'
            )
        )
    return Response(status=200)


@app.route("/roll_die", methods=["POST"])
@login_required
def roll_die():
    """Function to roll a die, if it's not already been rolled."""
    if not game.validate_user(current_user.get_id()):
        redirect(url_for('display_game'))
        return Response(status=400)

    power = int(request.form['power'])
    time_threshold = 0.5
    time_s = time_threshold/(1.2**power)
    time_factor = 1.3 - 0.002*power
    if game.players[0].die_roll == 0:
        with app.app_context():
            while time_s < time_threshold:
                sleep(time_s)
                turbo.push(
                    turbo.replace(
                        render_template(
                            'die_image.html',
                            die_number=randint(1,6)
                        ),
                        'die_image'
                    )
                )
                time_s *= time_factor

            game.players[0].reset_die()
            game.players[0].roll_die()
            turbo.push(
                turbo.replace(
                    render_template(
                        'die_image.html',
                        die_number=game.players[0].die_roll),
                        'die_image'
                )
            )

    if not game.check_if_moves_exist():
        message = {
            'title': "No Moves Available",
            'text': f"Sorry {game.players[0].colour}, you have no moves available!"
        }
        turbo.push(
            turbo.replace(
                render_template('popup.html', message=message),
                "popup_box"
            ),
            to=current_user.get_id()
        )
        game.players[0].reset_die()
        game.next_player()
        return Response(status=200)

    return redirect(url_for('display_game'))


@app.route("/close_popup", methods=["POST"])
def close_popup():
    """Function to close popup when okay button pressed."""
    turbo.push(
        turbo.replace(
            render_template('popup.html', message={}),
            'popup_box'
        ),
        to=current_user.get_id()
    )
    if game.players:
        die_number = game.players[0].die_roll
        player_colour = game.players[0].colour
    else:
        die_number = None
        player_colour = None

    turbo.push(
        turbo.replace(
            render_template(
                'controls.html',
                finished_tokens = game.finished_tokens,
                die_number = die_number,
                player_turn = player_colour,
                message={}
            ),
            'controls'
        )
    )
    if current_user.is_authenticated or request.form.get('type') == "new game":
        return redirect(url_for('display_game'))
    else:
        return Response(status=200)


@app.route("/quit_game", methods=["GET", "POST"])
@login_required
def quit_game():
    """Allows a player to leave the game."""
    if request.method == "GET":
        user_id = current_user.get_id()
        turbo.push(
            turbo.replace(
                render_template(
                    'popup.html',
                    message={
                        'title': "Quit Game",
                        'text': "This will remove you and all your counters from the board. Are you sure you want to leave?"
                    }
                ),
                "popup_box"
            ),
            to=user_id
        )
        return Response(status=200)

    elif request.method == "POST":
        user_id = current_user.get_id()
        game.remove_player(user_id)
        load_user(user_id).unauthenticate_user()
        if len(game.players) != 0:
            turbo.push(
                turbo.replace(
                    render_template(
                        'game.html',
                        counters = game.board,
                        finished_tokens = game.finished_tokens,
                        die_number = game.players[0].die_roll,
                        player_turn = game.players[0].colour,
                        message={}
                    ),
                    "game"
                )
            )
        return redirect(url_for('login'))


@app.route("/new_game", methods=["GET"])
@login_required
def new_game():
    """Called to start a new game, and unauthenticate all users."""
    global game
    # Game reset
    game = backend.Game()
    turbo.push(
        turbo.replace(
            render_template(
                'game.html',
                counters = game.board,
                finished_tokens = game.finished_tokens,
                die_number = 0,
                player_turn = "",
                message={
                    'title': 'New Game',
                    'text': 'A new game is starting.',
                    'type': 'new game'
                }
            ),
        'game'
        )
    )
    for user in users:
        user.unauthenticate_user()
    return redirect(url_for('login'), code=302)


if __name__ == "app":
    game = backend.Game()
