from functools import reduce
from strsimpy.weighted_levenshtein import WeightedLevenshtein
from strsimpy.string_distance import NormalizedStringDistance
from strsimpy.string_similarity import NormalizedStringSimilarity

def default_insertion_cost(interval):
    return 1.0

def default_deletion_cost(interval):
    return 1.0

def process_interval(interval):
    # TODO ask richard for help with docstring
    """
    Retrieve how wide the interval is based on the input.
    (for example, from M1 to 1, P3 to 3, -m2 to 2)
    :param str interval: The interval to be processed.
    :return: if the interval is represented with numbers, return itself,
    else, process the interval into the number
    """
    if interval[0].isalpha():
        interval = interval[1:]
    elif len(interval) > 1 and interval[1].isalpha():
        interval = interval[0] + interval[2:]
    else:
        pass
    return interval

def default_substitution_cost(a, b, interval_type, directed):
    """
    This method calculate how much different two interval is based on
    their type (whether they are directed or not).
    :param a: interval a
    :param b: interval b
    :param interval_type: the type of intervals this object would be used on: 'd' for
    diatonic intervals, 'z' for zero-indexed diatonic intervals, and 'c' for chromatic
    intervals.
    :param directed: defaults to True which shows that the voice that is lower on the staff is a
    higher pitch than the voice that is higher on the staff. This is designated with a "-" prefix.
    :return: a corresponding different score.
    """
    # TODO ask richard for help with correct calculation

    a = process_interval(a)
    b = process_interval(b)

    if interval_type == 'd':
        if directed:
            # for a diatonic and directed interval, the possible values includes everything
            # but 0 from -8 to 8 (inclusive) . This is calculated so that the substitution
            # -8 and 8 is given the score 1.
            if int(a) * int(b) > 0:
                return (abs(int(a) - int(b) + 1) / 8) * 0.5
            else:
                return (abs(int(a) - int(b)) / 8) * 0.5
        else:
            # for a diatonic and undirected interval, the possible values are
            # range from 1 to 8 (inclusive). This is calculated so that the substitution
            # 1 and 8 is given the score 1.
            return abs(int(a) - int(b) + 1) / 8
    elif interval_type == 'z':
        if directed:
            # for a zero-indexed, diatonic, and directed interval, the possible values includes
            # everything between -8 to 8 (inclusive). This is calculated so that the substitution
            # -7 and 7 is given the score 1.
            return abs(int(a) - int(b) + 1) / 15
        else:
            # for a zero-indexed, diatonic, and directed interval, the possible values includes
            # everything between 0 to 7 (inclusive). This is calculated so that the substitution
            # 0 and 7 is given the score 1.
            return abs(int(a) - int(b) + 1) / 8
    else:  # interval_type == 'c':
        if directed:
            # for a chromatic, and directed interval, the possible values includes
            # everything between -12 to 12 (inclusive) but 0. This is calculated so that the substitution
            # -12 and 12 is given the score 1.
            if int(a) * int(b) > 0:
                return (abs(int(a) - int(b) + 1) / 12) * 0.5
            else:
                return (abs(int(a) - int(b)) / 12) * 0.5
        else:
            # for a chromatic, and undirected interval, the possible values includes
            # everything between 1 to 12 (inclusive) but 0. This is calculated so that the substitution
            # 1 and 12 is given the score 1.
            return abs(int(a) - int(b) + 1) / 12

class WeightedIntervalLevenshtein(WeightedLevenshtein):
    """
    This class contains the methods to calculate a how similar two
    interables are using a weighted Levenshtein algorithm, and
    the users can customize how much weight each operation is worth.
    """
    def __init__(self, interval_type, directed,
                 substitution_cost_fn=default_substitution_cost,
                 insertion_cost_fn=default_insertion_cost,
                 deletion_cost_fn=default_deletion_cost):
        """
        This method create an instance of a weighted levenshtein object used for intervals.
        :param interval_type: The type of intervals this object would be used on: 'd' for
        diatonic intervals, 'z' for zero-indexed diatonic intervals, and 'c' for chromatic intervals.
        :param directed: defaults to True which shows that the voice that is lower on the staff is a
        higher pitch than the voice that is higher on the staff. This is designated with a "-" prefix.
        :param substitution_cost_fn: the function that decides how much weight does each substitution
        accounts for. (see default_substitution_cost()'s docstring for more)
        :param insertion_cost_fn: the function that decides an insertion's weight. (default to 1)
        :param deletion_cost_fn: the function that decides a deletion's weight. (default to 1)
        """
        WeightedLevenshtein.__init__(self, substitution_cost_fn=substitution_cost_fn,
                                    insertion_cost_fn=insertion_cost_fn,
                                    deletion_cost_fn=deletion_cost_fn)
        self.interval_type = interval_type
        self.directed = directed

    def distance(self, s0, s1):
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
                    cost = self.substitution_cost_fn(s0i, s1j, interval_type=self.interval_type,
                                                     directed=self.directed)
                insertion_cost = self.insertion_cost_fn(s1j)
                v1[j + 1] = min(v1[j] + insertion_cost, v0[j + 1] + deletion_cost, v0[j] + cost)
            v0, v1 = v1, v0

        return v0[len(s1)]

class NormalizedWeightedIntervalLevenshtein(NormalizedStringDistance, NormalizedStringSimilarity):
    """
    This class contains the methods allowing users to calculate and normalize the weighted Levenshtein
    score for a pair of interables of intervals.
    """
    def __init__(self, interval_type, directed, substitution_cost_fn=default_substitution_cost,
                insertion_cost_fn=default_insertion_cost, deletion_cost_fn=default_deletion_cost):
        """
        This method create an instance of a normalized weighted levenshtein object used for intervals.
        :param interval_type: The type of intervals this object would be used on: 'd' for
        diatonic intervals, 'z' for zero-indexed diatonic intervals, and 'c' for chromatic intervals.
        :param directed: defaults to True which shows that the voice that is lower on the staff is a
        higher pitch than the voice that is higher on the staff. This is designated with a "-" prefix.
        :param substitution_cost_fn: the function that decides how much weight does each substitution
        accounts for. (see default_substitution_cost()'s docstring for more)
        :param insertion_cost_fn: the function that decides an insertion's weight. (default to 1)
        :param deletion_cost_fn: the function that decides a deletion's weight. (default to 1)
        """

        self.levenshtein = WeightedIntervalLevenshtein(
            interval_type=interval_type, directed=directed,
            substitution_cost_fn=substitution_cost_fn,
            insertion_cost_fn=insertion_cost_fn,
            deletion_cost_fn=deletion_cost_fn
        )

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
