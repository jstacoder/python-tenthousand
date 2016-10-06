import time
import random
from scoring import score_roll, choose_dice
from players import get_player

class Game(object):
    _players = None
    _current = None
    _playing = False
    _last_turn = False

    def __init__(self,*players):
        self._players = players
        self._select_current()
        self.play()

    def _set_last_turn(self):
        self._last_turn = True

    def _is_last_turn(self):
        return self._last_turn

    def _select_current(self):
        self._current = random.choice(
                self._players
        )

    def play(self):
        try:
            self._playing = True
            while self._playing:
                if not self._is_last_turn():
                    if self._current.do_turn(self):
                        continue
                    else:
                        self._switch_players()
                else:
                    if self._current.do_last_turn(self):
                        continue
                    else:
                        self._switch_players()
        except KeyboardInterrupt:
            print "ok quitting now"
            import sys
            sys.exit(1)
        else:
            self._display_winner()

    def _display_winner(self):
        winner = self._determine_winning_player()
        print "{0.name} has won the game by scoring {0.score} points".format(winner)

    def _determine_winning_player(self):
        winner = None
        high_score = 0
        for player in self._players:
            player_score = player._get_score()
            if player_score > high_score:
                high_score = player_score
                winner = player
        return winner

    def _switch_players(self):
        self._current = self._players[self._get_next()]

    def _get_next(self):
        curr = self._players.index(
                self._current
        )
        if curr == len(self._players) - 1:
            curr = 0
        else:
            curr += 1
        return curr


def main():
    comp = get_player('comp1')
    kyle = get_player('kyle',True)

    players = [kyle,comp]
    game = Game(*players)

if __name__ == "__main__":
    main()
