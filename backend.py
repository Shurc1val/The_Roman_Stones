"""Module containing backend workings of the game."""

from random import randint

class Player():
    """Class for player instances."""
    def __init__(self, colour: str) -> None:
        self.colour = colour
        self.die_roll = 0

    def roll_die(self):
        """Function to randomly roll die if it is currently zero."""
        if self.die_roll == 0:
            self.die_roll = randint(1,6)

    def reset_die(self):
        self.die_roll = 0


class Game():
    """Class for game instance."""

    def __init__(self, counters_per_player: int) -> None:
        self.players = []
        self.counters_per_player = counters_per_player
        self.board = [[] for i in range(28)]
        self.finished_tokens = []

    def add_player(self, player: Player):
        """Function to add player to the board."""
        self.players.append(player)
        for i in range(self.counters_per_player):
            self.board[0].append(player.colour)


    @property
    def number_of_players(self) -> int:
        """Number of players on the board."""
        return len(self.players)


    @property
    def total_number_of_counters(self) -> int:
        """Total number of counters on the board."""
        return self.number_of_players * self.counters_per_player
    

    def _validate_move(self, current_index: int, colour: str) -> bool:
        """Function to validate a move is valid."""
        if (colour != self.players[0].colour) or (self.players[0].die_roll == 0):
            return False
        
        die_roll = self.players[0].die_roll
        
        if current_index + die_roll > 28:
            return False

        for place in self.board[current_index+1:current_index+die_roll]:
            if place.count(colour) < len(place) - 1:
                return False
            
        return True


    def _next_player(self):
        player = self.players.pop(0)
        self.players.append(player)


    def move_piece(self, current_index: int, colour: str) -> bool:
        """Function to attempt to move a counter on the board."""
        if not self._validate_move(current_index, colour):
            return False
        
        die_roll = self.players[0].die_roll

        self.board[current_index].remove(colour)

        
        for i in range(current_index+1, current_index+die_roll):
            for counter in self.board[i]:
                if (counter != colour) and (i % 7 != 0):
                    self.board[i].remove(counter)
                    self.board[0].append(counter)

        if current_index + die_roll == 28:
            self.finished_tokens.append(colour)
        else:
            self.board[current_index + die_roll].append(colour)

        self.players[0].reset_die()
        self._next_player()

        return True

        


def validate_user_input(msg, options):
    while True:
        user_input = input(msg)
        if user_input in options:
            return user_input
        print("Not a valid entry!\n")


def roll_die():
    return randint(1,6)


def validate_move(current_index, num, colour):
    if board[current_index].count(colour) == 0:
        return False
    for place in board[current_index+1:current_index+num]:
        if len(place) > 1 and place.count(colour) != len(place):
            return False
    if current_index + num > 28:
        return False
    return True


def move_piece(current_index, num, colour):
    board[current_index].remove(colour)
    if current_index + num == 28:
        finished_tokens.append(colour)
    else:
        board[current_index + num].append(colour)
    for i in range(current_index+1,current_index+num):
        if board[i] and i not in (7,14,21):
            for piece in board[i]:
                if piece != colour:
                    board[i].remove(piece)
                    board[0].append(piece)
    #Might cause errors at end of board
    return True


def main():
    board = [[] for i in range(28)]
    finished_tokens = []
    possible_colours = ["Blue","Green","Red","White"]
    user_num_to_index = {"s1":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"s2":7,"7":8,"8":9,"9":10,"10":11,"11":12,"12":13,"s3":14,"13":15,"14":16,"15":17,"16":18,"17":19,"18":20,"s4":21,"19":22,"20":23,"21":24,"22":25,"23":26,"24":27}
    players = []
    turn_counter = 1

    num_players = int(validate_user_input("Please enter the number of players (2-4): ", "234"))
    num_tokens = int(validate_user_input("How many tokens should each player have? (1-3) ", "123"))

    for i in range(1,num_players + 1):
        player_colour = validate_user_input(f"Player {i}, what colour do you want to be? ({', '.join(possible_colours)}) ", possible_colours)
        players.append(player_colour)
        possible_colours.remove(player_colour)
        for i in range(num_tokens):
            board[0].append(player_colour[0])

    print_board(board)

    while not max([finished_tokens.count(colour[0]) for colour in players]) == num_tokens:
        print("\n{} player turn".format(players[turn_counter-1]))
        input("Press any [enter] to roll the die: ")
        die_roll = roll_die()
        print(die_roll)
        while True:
            move_possible = False
            for i in range(0,28):
                if validate_move(i,die_roll,players[turn_counter-1][0]):
                    move_possible = True
            if move_possible:
                current_index = user_num_to_index[validate_user_input("Which piece would you like to move? (enter place name) ", user_num_to_index.keys())]
                if validate_move(current_index,die_roll,players[turn_counter-1][0]):
                    move_piece(current_index,die_roll,players[turn_counter-1][0])
                    break
                print("Not a valid move")
            else:
                print("No moves possible!!")
                input("(press [enter] to continue)")
                break
        print_board(board)
        turn_counter = (turn_counter + 1) % num_players

    print(f"Congratulations {players[turn_counter-1]} player, you win!!")