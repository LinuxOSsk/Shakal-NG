# -*- coding: utf-8 -*-
import bisect
import itertools
import random


def weighted_sample(items, weights, count):
	items = list(items)
	weights = list(weights)

	ret = []
	while count > len(ret):
		if len(items) < 1:
			ret.append(items[0])
			items = items[1:]
		else:
			acu_weights = list(itertools.accumulate(weights))
			max_value = acu_weights[-1]
			if isinstance(max_value, float):
				random_value = random.random() * max_value
			else:
				random_value = random.randint(0, max_value - 1)
			idx = bisect.bisect(acu_weights, random_value, hi=len(items) - 1)
			ret.append(items[idx])
			items.pop(idx)
			weights.pop(idx)

	return ret


random.choices
