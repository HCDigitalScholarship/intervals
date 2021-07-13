from strsimpy.weighted_levenshtein import WeightedLevenshtein

def insertion_cost(char):
    return 1.0

def deletion_cost(char):
    return 1.0

def substitution_cost(char_a, char_b):
    # TODO taking into account the 16 interval settings to normalize
    if char_a == 't' and char_b == 'r':
        return 0.5
    return 1.0

weighted_levenshtein = WeightedLevenshtein(
    substitution_cost_fn=substitution_cost,
    insertion_cost_fn=insertion_cost,
    deletion_cost_fn=deletion_cost)

print(weighted_levenshtein.distance('String1', 'String2'))