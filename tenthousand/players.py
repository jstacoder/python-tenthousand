from time import sleep
import random
from scoring import score_roll, choose_dice

roll = lambda n=6: [ random.choice(range(1,7)) for d in range(n) ]

has_die = lambda roll, die: die in roll

pull_held = lambda roll,choices: [x for x in roll if x in choices]

hold = lambda roll, choices: filter(lambda c: has_die(roll,c) and roll.pop(roll.index(c)) is not None,choices) 

def add_to_held(choices,held):
    for c in choices:
        held.append(c)
    
def remove_from_roll(choices,roll):
    new_roll = []
    for itm in choices:
        if itm in roll:
            idx = roll.index(itm)
            roll.pop(idx)
            new_roll.append(itm)
    return new_roll

class Player(object):

    def __init__(self,name):
        self.score = 0
        self.name = name
        self.on_last_turn = False
        self._reset_turn_data()

    def _reset_turn_data(self):
        self.tmp_score = 0
        self.roll = None
        self.held = None

    def _get_score(self):
        return self.score

    def _display_to_screen(self,msg):
        print msg
        sleep(2)

    def choose_dice_to_hold(self,roll):
        print 'checking what to hold from {}'.format(self._format_roll(roll))
        choice = choose_dice(roll)
        print "{} chose {}".format(self.name,self._format_roll(choice))
        return choice

    def get_roll(self):
        return self._format_roll(self.roll)

    def _format_roll(self,dice):
        return ','.join(map(str,dice))

    def _ask_to_keep_rolling(self):
        return random.choice(['y','n'])

    def do_turn(self,game):
        self._display_to_screen('ok its {0}\'s turn to roll\n{0}\'s score is {1}'.format(self.name,self.score))
        keep_rolling = None
        
        # initalize values
        self.roll = [] if self.roll is None else self.roll
        self.held = [] if self.held is None else self.held
        old_held = self.held
        tmp_score = 0

        # first get inital roll
        self.roll = roll(len(self.roll) or 6)
        self._display_to_screen("i just rolled {}".format(self.get_roll()))
        # then check what to keep
        holding = self.choose_dice_to_hold(self.roll)
        tmp_score = score_roll(holding)
        self.tmp_score += tmp_score

        # check if anything was picked up, turn over if not
        held_count = len(holding)
        held_copy = list(holding)
        remove_from_roll(pull_held(self.roll,holding),self.roll)
        
        for itm in held_copy:
            self.held.append(itm)

        if held_count:
            self._display_to_screen("{} is holding {} worth {} points".format(self.name,self._format_roll(held_copy),tmp_score))
            self._display_to_screen("{} is now holding {} worth a total of {} points".format(self.name,self._format_roll(self.held),self.tmp_score))
            # then check if score >= 1000
            if self.score < 1000 and self.tmp_score < 1000:
                # must keep rolling until 1000 points is reached
                print "{} only has {} points, i need to keep rolling until i hit 1000".format(self.name,self.tmp_score)
                keep_rolling = True
            else:
                # check if any dice were not picked up, if all 6 were picked up we need to roll again
                if len(self.roll):
                    print "Ok, {} can stay, keep rolling .... ?".format(self.name)
                    computer_choice = self._ask_to_keep_rolling()
                    keep_rolling = computer_choice == 'y' 
                    print "the computer chose to {} rolling".format({'y':'keep','n':'stop'}[computer_choice])
                    if keep_rolling is not None and not keep_rolling:
                        self.score += self.tmp_score
                        self.tmp_score = 0
                        self._display_to_screen("{} now has {} points".format(self.name,self.score))
                        self._reset_turn_data()
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
                print "nothing picked up!! {}'s turn is over!!".format(self.name)
                self._reset_turn_data()
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
