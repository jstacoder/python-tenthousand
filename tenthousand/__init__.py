import time
import random
from scoring import score_roll, choose_dice

roll = lambda n=6: [ random.choice(range(1,7)) for d in range(n) ]

has_die = lambda roll, die: die in roll

hold = lambda roll, choices: filter(lambda c: has_die(roll,c) and roll.pop(roll.index(c)) is not None,choices) 

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

class Player(object):
	roll = None
	held = None
	on_last_turn = False
	
	def __init__(self,name):
		self.score = 0
		self.tmp_score = 0
		self.name = name

	def _get_score(self):
		return self.score
	
	def choose_dice_to_hold(self,roll):
		return choose_dice(roll)

	def do_turn(self,game):
		keep_rolling = None
		# initalize values
		self.roll = [] if self.roll is None else self.roll
		self.held = [] if self.held is None else self.held
		old_held = self.held
		tmp_score = 0
		
		# first get inital roll
		self.roll = roll(len(self.roll) or 6)	

		# then check what to keep
		holding = self.choose_dice_to_hold(self.roll)
		
		tmp_score = score_roll(holding)
		self.tmp_score += tmp_score
		
		# check if anything was picked up, turn over if not
		held_count = len(holding)
		self.held += hold(self.roll,holding)
		if held_count:
			# then check if score >= 1000
			if self.score < 1000 and self.tmp_score < 1000:
				# must keep rolling until 1000 points is reached
				print "i only have {} points, i need to keep rolling until i hit 1000".format(self.tmp_score)
				keep_rolling = True
			else:
				# check if any dice were not picked up, if all 6 were picked up we need to roll again
				if len(self.roll):
					print "Ok, you can stay, will you keep rolling .... ?"
					computer_choice = self._ask_to_keep_rolling()
					keep_rolling = computer_choice == 'y' 
					print "the computer chose to {} rolling".format({'y':'keep','n':'stop'}[computer_choice])
				else:
					print "no dice left, must keep rolling"
					keep_rolling = True
					
		else:
			# check matching doubles
			if self._check_for_matching_doubles():
				print "you have doubles, roll again"
				keep_rolling = True
			else:
			# nothing picked up, end turn
				print "nothing picked up!! turn over!!"
				keep_rolling = False
		return keep_rolling if keep_rolling is not None else False
		
	
	def _check_for_matching_doubles(self):
		return (len(self.roll) == 2) and (self.roll[0] == self.roll[1])
		
	
	def _do_turn(self,game):
		score = self._get_score()
		self.score += score
		print "its {}'s turn, he scored {}, now he has {} points".format(self.name,score,self.score)
		if self.score >= 40:
			game._playing = False
			print "{} won!!!".format(self.name)
		time.sleep(.5)
		return score == 5 #False

class HumanPlayer(Player):
	
	def do_last_turn(self,game):
		#self.on_last_turn = True
		return self.do_turn(game)


	def do_turn(self,game):
		if self.on_last_turn:			
			game._playing = False
			return False
		print "{}, press enter to roll\n".format(self.name)
		raw_input()
		self.roll = [] if self.roll is None else self.roll
		self.held = [] if self.held is None else self.held
		old_held = self.held
		self.roll = roll(len(self.roll) or 6)
		print "you rolled {}".format(','.join(map(str,self.roll)))
		holding = []
		choice = True
		while choice != '\n' and  choice != '':
			print "type a number and press enter to hold it\n"
			choice = raw_input()
			if choice and choice != '\n':	
				try:
					holding.append(int(choice))
				except ValueError:
					print "please enter a number"
				
		tmp_score = score_roll(holding)
		self.tmp_score += tmp_score
		held_count = len(holding)
		held_copy = list(holding)
		self.held += hold(self.roll,holding)
		print "held {}, worth {} points".format(','.join(map(str,held_copy)),tmp_score)
		print "your holding {},\nworth {} points".format(','.join(map(str,self.held)),self.tmp_score)
		if held_count:
			if self.score < 1000 and self.tmp_score < 1000:
				print "you need 1000 points to keep anything"
				keep_rolling = 'y'
			else:
				if len(self.roll):
					print "keep rolling? y/n\n"
					keep_rolling = raw_input()
				else:
					print "no dice left, must keep rolling"
					return True	
		else:
			if self._check_for_matching_doubles():
				print "you have doubles, roll again"
				return True	
			print "nothing held!\nturn over"
			self.tmp_score = 0
			keep_rolling = 'n'
		if keep_rolling == 'y':
			return True
		else:
			self.roll = None
			self.held = None
			self.score += self.tmp_score
			self.tmp_score = 0
			print "now you have {} points".format(self.score)
			if self.score >= 10000:
				if not self.on_last_turn:
					print "{} has over 10,000 points!! that means this is the last round.".format(self.name)
					game._set_last_turn()
					self.on_last_turn = True				
			return False
		#return super(HumanPlayer,self).do_turn(game)
		
		

def main():
	comp = Player('comp1')
	kyle = HumanPlayer('kyle')
	joe = HumanPlayer('joe')
	eric = HumanPlayer('eric')
	h = HumanPlayer('jake')
	
	players = [kyle,joe,eric,h,comp]
	#print random.choice(players).name
	game = Game(*players)
	
if __name__ == "__main__":
	main()

