import time
import random
from scoring import score_roll, choose_dice
from players import Player, HumanPlayer

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
	comp = Player('comp1')
	kyle = Player('kyle')
	
	players = [kyle,comp]
	game = Game(*players)
	
if __name__ == "__main__":
	main()
