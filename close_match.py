"""
This code contains...
"""

from functools import reduce
from strsimpy.weighted_levenshtein import WeightedLevenshtein
from strsimpy.string_distance import NormalizedStringDistance
from strsimpy.string_similarity import NormalizedStringSimilarity

def default_insertion_cost(interval):
    return 1.0

def default_deletion_cost(interval):
    return 1.0

def default_substitution_cost(a, a_index, b, b_index):
    return 1.0

def test_substitution_cost(a, a_index,b, b_index):
    if a_index == b_index == 0:
        return 0.0
    else:
        return 1.0

class WeightedIntervalLevenshtein(WeightedLevenshtein):
    """
    This class contains the methods to calculate a how similar two
    iterables are using a weighted Levenshtein algorithm, and
    the users can customize how much weight each operation is worth.
    """
    def __init__(self, substitution_cost_fn=default_substitution_cost, insertion_cost_fn=default_insertion_cost,
                 deletion_cost_fn=default_deletion_cost):
        """
        This method create an instance of a weighted levenshtein object used for intervals.
        diatonic intervals, 'z' for zero-indexed diatonic intervals, and 'c' for chromatic intervals.
        higher pitch than the voice that is higher on the staff. This is designated with a "-" prefix.
        :param substitution_cost_fn: the function that decides an insertion's weight. (default to 1)
        :param insertion_cost_fn: the function that decides an insertion's weight. (default to 1)
        :param deletion_cost_fn: the function that decides a deletion's weight. (default to 1)
        """
        WeightedLevenshtein.__init__(self, substitution_cost_fn=substitution_cost_fn,
                                    insertion_cost_fn=insertion_cost_fn,
                                    deletion_cost_fn=deletion_cost_fn)

    def distance(self, s0, s1):
        """
        Calculate how different two interble of intervals are.
        :param s0: first interable of interval
        :param s1: second interable of interval
        :return: a distance score
        """
        if s0 is None:
            raise TypeError("Argument s0 is NoneType.")
        if s1 is None:
            raise TypeError("Argument s1 is NoneType.")
        if s0 == s1:
            return 0.0
        if len(s0) == 0:
            return reduce(lambda cost, char: cost + self.insertion_cost_fn(char), s1, 0)
        if len(s1) == 0:
            return reduce(lambda cost, char: cost + self.deletion_cost_fn(char), s0, 0)

        v0, v1 = [0.0] * (len(s1) + 1), [0.0] * (len(s1) + 1)

        v0[0] = 0
        for i in range(1, len(v0)):
            v0[i] = v0[i - 1] + self.insertion_cost_fn(s1[i - 1])

        for i in range(len(s0)):
            s0i = s0[i]
            deletion_cost = self.deletion_cost_fn(s0i)
            v1[0] = v0[0] + deletion_cost

            for j in range(len(s1)):
                s1j = s1[j]
                cost = 0
                if s0i != s1j:
                    cost = self.substitution_cost_fn(s0i, i, s1j, j)
                insertion_cost = self.insertion_cost_fn(s1j)
                v1[j + 1] = min(v1[j] + insertion_cost, v0[j + 1] + deletion_cost, v0[j] + cost)
            v0, v1 = v1, v0

        return v0[len(s1)]

class NormalizedWeightedIntervalLevenshtein(NormalizedStringDistance, NormalizedStringSimilarity):
    """
    This class contains the methods allowing users to calculate and normalize the weighted Levenshtein
    score for a pair of iterables of intervals.
    """
    def __init__(self, substitution_cost_fn=default_substitution_cost,
                 insertion_cost_fn=default_insertion_cost, deletion_cost_fn=default_deletion_cost):
        """
        This method create an instance of a normalized weighted levenshtein object used for intervals.
        diatonic intervals, 'z' for zero-indexed diatonic intervals, and 'c' for chromatic intervals.
        higher pitch than the voice that is higher on the staff. This is designated with a "-" prefix.
        :param substitution_cost_fn: the function that decides how much weight does each substitution
        accounts for. (see default_substitution_cost()'s docstring for more)
        :param insertion_cost_fn: the function that decides an insertion's weight. (default to 1)
        :param deletion_cost_fn: the function that decides a deletion's weight. (default to 1)
        """

        self.levenshtein = WeightedIntervalLevenshtein(substitution_cost_fn=substitution_cost_fn,
                                                       insertion_cost_fn=insertion_cost_fn,
                                                       deletion_cost_fn=deletion_cost_fn)

    def distance(self, s0, s1):
        """
        Calculate how different two iterble of intervals are.
        :param s0: first iterable of interval
        :param s1: second iterable of interval
        :return: a distance score
        """
        if s0 is None:
            raise TypeError("Argument s0 is NoneType.")
        if s1 is None:
            raise TypeError("Argument s1 is NoneType.")
        if s0 == s1:
            return 0.0
        m_len = max(len(s0), len(s1))
        if m_len == 0:
            return 0.0
        lev = self.levenshtein.distance(s0, s1)
        return  lev / m_len

    def similarity(self, s0, s1):
        """
        Calculate how similar two interbles of intervals are.
        :param s0: first interable of interval
        :param s1: second interable of interval
        :return: a similarity score
        """
        return 1.0 - self.distance(s0, s1)

wl = WeightedIntervalLevenshtein(substitution_cost_fn=test_substitution_cost)
nwl = NormalizedWeightedIntervalLevenshtein()
print(wl.distance(['P8', 'P5', 'P8', 'P5', 'P8'], ['P10', 'P5', 'P8', 'P5', 'P8']))
print(nwl.similarity(['P8', 'P5', 'P8', 'P5', 'P8'], ['P10', 'P5', 'P8', 'P5', 'P8']))

"""
# modules
['7_Held', '6_Held', '6_Held', '5_-2', '8'], ['5_Held', '6_-2', '7_Held', '6_-3', '8']
['7_Held', '6_Held', '6_Held', '5_-2', '8'], ['7_Held', '6_Held', '6_Held', '5_-2', '8']

# notes, q 
# directed 
['P8', 'P5', 'P8', 'P5', 'P8'], ['P8', 'M10', 'P1', 'M2', 'M3']
['-M2', '-P5', '-M6', '-m3', '-m3'], ['m10', 'M10', 'm10', 'P12', 'P11']
['-M2', '-P5', '-M6', '-m3', '-m3'], ['-M2', '-P5', '-M6', '-m3', '-m3']

# undirected
['P5', 'M10', 'M9', 'P8', 'M7'], ['M10', 'P5', 'P8', 'P5', 'P8']

# notes, 'd'
['3', '3', '3', '3', '3'], ['8', '10', '1', '2', '3']

# notes, c
['19', '19', '15', '16', '20'], ['7', '3', '0', '3', '1']
['12', '10', '15', '10', '-5'], ['3', '12', '14', '12', '15']
"""
