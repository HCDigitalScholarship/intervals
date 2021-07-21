from functools import reduce
from strsimpy.string_distance import NormalizedStringDistance
from strsimpy.string_distance import StringDistance
from strsimpy.string_similarity import NormalizedStringSimilarity

def default_insertion_cost(interval):
    return 2.0

def default_deletion_cost(interval):
    return 2.0

def process_interval(interval):
    if interval[0].isalpha():
        interval = interval[1:]
    elif len(interval) > 1 and interval[1].isalpha():
        interval = interval[0] + interval[2:]
    else:
        pass
    return interval

def default_substitution_cost(a, b, interval_type='d'):
    # process a and b so that they could be converted to int

    a = process_interval(a)
    b = process_interval(b)

    if interval_type == 'd':
        return abs(int(a) - int(b)) / 8
    else:  # interval_type == 'c':
        return abs(int(a) - int(b)) / 12

class WeightedIntervalLevenshtein(StringDistance):

    def __init__(self, interval_type,
                 substitution_cost_fn=default_substitution_cost,
                 insertion_cost_fn=default_insertion_cost,
                 deletion_cost_fn=default_deletion_cost,
                 ):
        self.substitution_cost_fn = substitution_cost_fn
        self.insertion_cost_fn = insertion_cost_fn
        self.deletion_cost_fn = deletion_cost_fn
        self.interval_type = interval_type

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
                    cost = self.substitution_cost_fn(s0i, s1j, interval_type=self.interval_type)
                insertion_cost = self.insertion_cost_fn(s1j)
                v1[j + 1] = min(v1[j] + insertion_cost, v0[j + 1] + deletion_cost, v0[j] + cost)
            v0, v1 = v1, v0

        return v0[len(s1)]

class NormalizedWeightedIntervalLevenshtein(NormalizedStringDistance, NormalizedStringSimilarity):
    # not allow users to choose score metrix for normalized method because different length division!
    def __init__(self, interval_type):
        self.levenshtein = WeightedIntervalLevenshtein(
            interval_type=interval_type,
            substitution_cost_fn=default_substitution_cost,
            insertion_cost_fn=default_insertion_cost,
            deletion_cost_fn=default_deletion_cost
        )

    def distance(self, s0, s1):
        if s0 is None:
            raise TypeError("Argument s0 is NoneType.")
        if s1 is None:
            raise TypeError("Argument s1 is NoneType.")
        if s0 == s1:
            return 0.0
        m_len = max(len(s0), len(s1))
        if m_len == 0:
            return 0.0
        # normalized distance is distance/2*length because deletion score = insertion score = 2
        # while substition score ranges from 0-2
        lev = self.levenshtein.distance(s0, s1)
        return  lev / (m_len*2)

    def similarity(self, s0, s1):
        return 1.0 - self.distance(s0, s1)
nwl = NormalizedWeightedIntervalLevenshtein(interval_type='d')
# print("nwl similarity", nwl.similarity(('1', '2', '3', '4'), ('1', '2', '3', '-4')))
# print("nwl similarity", nwl.similarity(('1', '2', '3', '4'), ('1', '2', '3', '5')))
# print("nwl similarity", nwl.similarity(('1', '2', '3', '4'), ('1', '2', '3', '6')))
