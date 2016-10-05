from functools import partial

def score_n_of_a_kind(n,nums,num):
	base_table = {x : 100 if x != 1 else 1000 for x in range(1,7) }
	base = base_table[num]
	score = get_score(n,num*base)
	check_func = check_n_funcs[str(n)]
	return score if check_func(nums,num) else 0
	
def _get_n_of_a_kind_scores(nums):
	results = { str(n) : 0 for n in range(1,7) }
	for k in results.keys():
		for check in range(3,7):
			_k = int(k)
			if not results[k]:
				results[k] = score_n_of_a_kind(check,nums,_k)
	return results

def get_score(num,base):
	n = num - 3
	for x in range(n):
		base += base
	return base


def score_roll(roll):
	score = 0
	score = score_strait(roll)
	score = score or score_doubles(roll)
	if not score:
		score = score_3_or_more_of_a_kind(roll)
		score += score_fives(roll)
		score += score_ones(roll)
	return score

def check_3_or_more(roll,n):
	rtn = None
	for func_num in check_n_funcs:
		func = check_n_funcs[func_num]
		if func(roll,n):
			rtn = [n] * count(roll,n)
	return rtn


def choose_dice(roll):
	if check_doubles(roll) or check_strait(roll):
		return roll
	else:
		rtn = []
		three_or_mores = get_3_or_more_from_roll(roll)
		if three_or_mores:
			for result in three_or_mores:
				rtn.extend(result)
		counts = {
			'1' : check_ones(roll),
			'5' : check_fives(roll)
		}
		for n in counts:
			for x in range(counts[n]):
				rtn.append(int(n))
		return rtn
		
get_3_or_more_from_roll = lambda roll: filter(None, map(lambda x: check_3_or_more(roll,x),range(1,7)))

single_bases = {1:100,5:50}

count = lambda lst,n: len(filter(lambda x: x == n,lst))

check_strait = lambda nums: all(map(lambda n: n == 1, map(lambda x: count(nums,x),range(1,7))))

check_doubles = lambda nums: len(filter(lambda x: x == 2,map(lambda n: count(nums,n),range(1,7)))) == 3	

check_n_or_more = lambda n,nums,num: count(nums,num) == n

check_n_funcs = { str(n) : partial(check_n_or_more,n) for n in range(3,7) }

check_single = lambda n,roll: count(roll,n) if count(roll,n) > 0 and count(roll,n) < 3 else 0

check_fives = partial(check_single,5)

check_ones = partial(check_single,1)

score_check = lambda check_func, score, nums: score if check_func(nums) else 0

score_strait = partial(score_check,check_strait,1000)

score_doubles = partial(score_check,check_doubles,1000)

score_single = lambda n,roll: check_single(n,roll)*single_bases[n]

score_ones = partial(score_single,1)

score_fives = partial(score_single,5)

score_3_of_a_kind = partial(score_n_of_a_kind,3)

score_3_or_more_of_a_kind = lambda roll: sum(_get_n_of_a_kind_scores(roll).values())
