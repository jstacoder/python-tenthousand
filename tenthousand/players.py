import os
import random
from time import sleep
from scoring import score_roll, choose_dice

DEBUG = os.environ.get('DEBUG',False)

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

def get_player(name,human_player=False):
    player_type = 'ai' if not human_player else 'human'
    return player_types[player_type](name)

class Player(object):
    INITIAL_LIMIT = 1000
    MAX_SCORE = 10000
    
    def __init__(self,name):
        self.score = 0
        self.name = name
        self.on_last_turn = False
        self._reset_turn_data()
        
    def _set_initial_limit(self,limit):
        self.__class__.INITIAL_LIMIT = limit

    def _set_max_score(self,score):
        self.__class__.MAX_SCORE = score

    def _check_for_matching_doubles(self):
        return (len(self.get_roll()) == 2) and (self.get_roll()[0] == self.get_roll()[1])

    def _reset_turn_data(self):
        self.reset_tmp_score()
        self.roll = None
        self.held = None

    def _get_score(self):
        return self.score

    def _display_to_screen(self,msg):
        print msg
        sleep(1)
        
    def _display_score(self):
        self._display_to_screen("{} has {} points".format(self.name,self._get_score()))
        
    def get_roll(self):
        return self.roll
    
    def get_held(self):
        return self.held
    
    def display_roll(self,roll=None):
        return self._format_roll(roll or self.get_roll())
    
    def _display_roll(self,fmt=None,roll=None):
        fmt = fmt if fmt is not None else "{}"
        current_roll = roll if roll is not None else self.get_roll()
        msg = fmt.format(self._format_roll(current_roll))
        self._display_to_screen(msg)

    def _format_roll(self,dice):
        return ','.join(map(str,dice))
        
    def ask_to_keep_rolling(self):        
        return self._ask_to_keep_rolling()
    
    def score_roll(self,dice):
        return score_roll(dice)
    
    def update_tmp_score(self,score=0,reset=None):
        self.tmp_score = score + self.tmp_score if reset is None else score
        
    def reset_tmp_score(self):
        self.update_tmp_score(0,True)
        
    def update_score(self):
        self.score += self.tmp_score
        
    def add_to_held(self,die):
        self.held = self.get_held() if self.get_held() is not None else []
        self.held.append(die)
        
    def roll_dice(self,num=None,_roll=None):
        '''
            set instance roll attr
            either pass a roll which i just directly assigned  to self.roll (for testing)
            or generate a random roll of num dice and assign that 
        '''
        num = num if num is not None else (len(self.get_roll()) or 6)
        current_roll = _roll if _roll is not None else roll(num)
        self.roll = current_roll
        
    def score_under_initial_limit(self):
        return self.score < self.INITIAL_LIMIT and self.tmp_score < self.INITIAL_LIMIT
    
    def do_turn(self,game):
        '''
            abstract method
            main gameplay logic should be
            defined here, this is where the difference
            between human and pc comes through
        '''
        raise NotImplementedError
    
    def choose_dice_to_hold(self,roll=None):
        '''
            abstract method
            should return list of dice to remove from
            self.roll and add to self.held
            but this method should not add or remove anything
            from those attributes, just return the list of items
        '''
        raise NotImplementedError
    
    def _ask_to_keep_rolling(self):
        '''
            abstract method,
            should return a string
            either "y" for yes or True
            or "n" for no or False
        '''
        raise NotImplementedError
        
class ComputerPlayer(Player):
        
    def choose_dice_to_hold(self,roll=None):
        current_roll = roll if roll is not None else self.get_roll()
        if DEBUG:
            print 'checking what to hold from {}'.format(self.display_roll(current_roll))
        choice = self.choose_dice(current_roll)
        if DEBUG:
            print "{} chose {}".format(self.name,self._format_roll(choice))
        return choice
    
    def choose_dice(self,roll=None):
        return choose_dice(roll or self.get_roll())

    def _ask_to_keep_rolling(self):
        score = self._get_score() or 0
        return random.choice(['y','n']) if score > 0 else 'n'

    def do_turn(self,game):
        self._display_to_screen('ok its {0}\'s turn to roll\n{0}\'s score is {1}'
            .format(self.name,self.score))        
        keep_rolling = None
        # initalize values
        self.roll = [] if self.get_roll() is None else self.get_roll()
        self.held = [] if self.get_held() is None else self.get_held()
        old_held = self.held
        tmp_score = 0
        # first get inital roll
        self.roll_dice()
        dispay_str = "{} just rolled ".format(self.name) + "{}"
        self._display_roll(dispay_str)
        # then check what to keep
        holding = self.choose_dice_to_hold()
        tmp_score = self.score_roll(holding)
        self.update_tmp_score(tmp_score)
        # check if anything was picked up,
        # current turn is over if not        
        held_count = len(holding)
        held_copy = list(holding)
        remove_from_roll(pull_held(self.get_roll(),holding),self.get_roll())
        for itm in held_copy:
            self.add_to_held(itm)
        if held_count: # user held items this round
            self._display_to_screen("{} is picking up {} worth {} points".format(self.name,self._format_roll(held_copy),tmp_score))
            self._display_to_screen("{} is now holding {} worth a total of {} points".format(self.name,self._format_roll(self.get_held()),self.tmp_score))
            # then check if score >= 1000
            if self.score_under_initial_limit():
                # must keep rolling until 1000 points is reached
                print "{} only has {} points, they need to keep rolling until they hit 1000 points".format(self.name,self.tmp_score)
                keep_rolling = True
            else:
                # check if any dice were not picked up, if all 6 were picked up we need to roll again
                if len(self.get_roll()):
                    self._display_to_screen("Ok, {} can stay, keep rolling .... ?".format(self.name))
                    computer_choice = self._ask_to_keep_rolling()
                    keep_rolling = computer_choice == 'y'
                    print "{} has chosen to {} rolling".format(self.name,{'y':'continue','n':'stop'}[computer_choice])
                    if keep_rolling is not None and not keep_rolling:
                        self.update_score()
                        self.reset_tmp_score()
                        self._display_score()
                        self._reset_turn_data()
                else:
                    self._display_to_screen("no dice left to stay, {} must keep rolling".format(self.name))
                    keep_rolling = True
        else:
            # check matching doubles
            if self._check_for_matching_doubles():
                self._display_to_screen("you have doubles, roll again")
                keep_rolling = True
            else:
            # nothing picked up, end turn
                self._display_to_screen("nothing picked up!! {}'s turn is over!!".format(self.name))
                self._reset_turn_data()
                keep_rolling = False
        return keep_rolling if keep_rolling is not None else False

class HumanPlayer(Player):
    
    def _prompt_user(self,msg,format=None):
        print msg if format is None else msg.format(self)
        return raw_input()
    
    def choose_dice_to_hold(self,roll=None):        
        holding = []
        choice = True
        while choice != '\n' and  choice != '':
            choice = self._prompt_user("type a number and press enter to hold it\n")            
            if choice and choice != '\n':
                try:
                    holding.append(int(choice))
                except ValueError:
                    print "please enter a number"
        return roll or holding        
                
    def do_last_turn(self,game):
        return self.do_turn(game)

    def do_turn(self,game):
        if self.on_last_turn and self.score >= self.MAX_SCORE:
            game._playing = False
            return game._playing
        self._prompt_user("{0.name}, press enter to roll\n",True)        
        self.roll = [] if self.get_roll() is None else self.get_roll()
        self.held = [] if self.get_held() is None else self.get_held()
        old_held = self.held
        self.roll_dice()
        self._display_roll("you rolled {}")
        holding = self.choose_dice_to_hold()
        tmp_score = self.score_roll(holding)
        self.update_tmp_score(tmp_score)
        held_count = len(holding)
        held_copy = list(holding)
        remove_from_roll(pull_held(self.get_roll(),holding),self.get_roll())

        for itm in held_copy:
            self.add_to_held(itm)        
        if held_count:
            self._display_to_screen("{} is picking up {}, worth {} points".format(self.name,self._format_roll(held_copy),tmp_score))                                
            self._display_to_screen("your holding {},\nworth {} points".format(self._format_roll(self.get_held()),self.tmp_score))
            if self.score_under_initial_limit():
                self._display_to_screen("you need 1000 points to keep anything\nso you still need {} points to stay".format((1000-self.tmp_score)))
                keep_rolling = 'y'
            else:
                if len(self.get_roll()):
                    keep_rolling = self._prompt_user("keep rolling? y/n\n")                    
                else:
                    self._display_to_screen("no dice left, must keep rolling")
                    return True
        else:
            if self._check_for_matching_doubles():
                self._display_to_screen("you have doubles, roll again")
                return True
            self._display_to_screen("nothing held!\nturn over")
            self.reset_tmp_score()
            keep_rolling = 'n'
        if keep_rolling == 'y':
            return True
        else:
            self.update_score()
            self._reset_turn_data()
            self._display_score()
            if self._get_score() >= self.MAX_SCORE:
                if not self.on_last_turn:
                    self._display_to_screen("{} has over 10,000 points!! that means this is the last round.".format(self.name))
                    #game._set_last_turn()
                    self.on_last_turn = True
            return False

player_types = dict(human=HumanPlayer,ai=ComputerPlayer)