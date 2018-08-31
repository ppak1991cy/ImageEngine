import random


def random_pick(some_list, probablities):
    """ random pick according probablities """

    assert len(some_list) == len(probablities), "lenth of items and probablities is not equal"
    x = random.randint(0, 100)
    cumulative_probability = 0
    item = None
    for item, item_probability in zip(some_list, probablities):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            break

    return item
