"""Module containing backend workings of the game."""

from math import ceil, sqrt
from random import randint

class Player():
    """Class for player instances."""
    def __init__(self, colour: str, user_id: str) -> None:
        self.colour = colour
        self.die_roll = 0
        self.user_id = user_id

    def roll_die(self):
        """Function to randomly roll die if it is currently zero."""
        if self.die_roll == 0:
            self.die_roll = randint(1,6)

    def reset_die(self):
        self.die_roll = 0


class Game():
    """Class for game instance."""

    def __init__(self) -> None:
        self.players = []
        self.number_of_players = 0
        self.counters_per_player = 0
        self.board = [[None] * 9 for i in range(28)]
        self.finished_tokens = []


    def _remove_piece(self, colour, index):
        """Replaces counter at given index on board with None."""
        position = self.board[index].index(colour)
        self.board[index][position] = None

    
    def _add_piece(self, colour, index):
        """Replaces first None at given index on board with colour."""
        position = self.board[index].index(None)
        self.board[index][position] = colour

    
    def set_num_players_and_counters(self, number_of_players: int, counters_per_player: int):
        self.number_of_players = number_of_players
        self.counters_per_player = counters_per_player
        self.board = [[None] * (ceil(sqrt(self.total_number_of_counters))**2) for i in range(28)]


    def remove_player(self, user_id: str):
        """Removes a player from the game"""
        for player in self.players:
            if player.user_id == user_id:
                colour = player.colour
                self.players.remove(player)

        for square in self.board:
            for i, counter in enumerate(square):
                if counter == colour:
                    square[i] = None

        for counter in self.finished_tokens:
            if counter == colour:
                self.finished_tokens.remove(counter)
        
        self.number_of_players -= 1


    def add_player(self, player: Player):
        """Function to add player to the board."""
        self.players.append(player)
        for i in range(self.counters_per_player):
            self._add_piece(player.colour, 0)


    @property
    def player_ids(self) -> list[int]:
        """Returns list of user_id for all the players in the game."""
        return [player.user_id for player in self.players]


    @property
    def total_number_of_counters(self) -> int:
        """Total number of counters on the board."""
        return self.number_of_players * self.counters_per_player
    

    def _validate_user(self, user_id: str) -> bool:
        print(self.players[0].user_id, user_id)
        if self.players[0].user_id != user_id:
            return False
        
        return True


    def _validate_move(self, current_index: int, colour: str) -> bool:
        """Function to validate a move is valid."""
        if (colour != self.players[0].colour) or (self.players[0].die_roll == 0):
            return False
        
        die_roll = self.players[0].die_roll
        
        if current_index + die_roll > 28:
            return False

        for place in self.board[current_index+1:current_index+die_roll]:
            num_counters = len([counter for counter in place if counter])
            if (num_counters >= 2) and (place.count(colour) < num_counters):
                return False
            
        return True

    
    def check_if_moves_exist(self) -> bool:
        """Function to check if any moves are available for the current player."""
        colour = self.players[0].colour

        for i, place in enumerate(self.board):
            if (colour in place) and self._validate_move(i, colour):
                return True

        return False


    def next_player(self):
        player = self.players.pop(0)
        self.players.append(player)


    def check_win(self, colour: str) -> bool:
        """Function to check if the game has been won by a given colour."""
        if self.finished_tokens.count(colour) == self.counters_per_player:
            return True
        
        return False


    def move_piece(self, current_index: int, colour: str, user_id: str) -> bool:
        """Function to attempt to move a counter on the board."""
        if not (self._validate_user(user_id) and self._validate_move(current_index, colour)):
            return False
        
        die_roll = self.players[0].die_roll

        self._remove_piece(colour, current_index)

        for i in range(current_index + 1, current_index + die_roll):
            for counter in self.board[i]:
                if (counter != colour) and (i % 7 != 0):
                    self._remove_piece(counter, i)
                    self._add_piece(counter, 0)

        if current_index + die_roll == 28:
            self.finished_tokens.append(colour)
        else:
            self._add_piece(colour, current_index + die_roll)

        self.players[0].reset_die()
        self.next_player()

        return True
