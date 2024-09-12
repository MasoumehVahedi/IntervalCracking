

# ----------------------------------------------------------------------- #
#                            Interval (range [min, max])
# ----------------------------------------------------------------------- #

class Interval:
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val

    def __repr__(self):
        return f'[{self.min_val}, {self.max_val}]'


# ----------------------------------------------------------------------- #
#                           Interval Entry
# ----------------------------------------------------------------------- #

class IntervalTreeEntry:
    def __init__(self, interval, data=None, child=None):
        self.interval = interval
        self.data = data
        self.child = child

    def __repr__(self):
        return f'IntervalEntry({self.interval})'


# ----------------------------------------------------------------------- #
#                           Interval Node
# ----------------------------------------------------------------------- #

class IntervalTreeNode:
    def __init__(self, is_leaf=True, parent=None, level=0):
        self.entries = []
        self.is_leaf = is_leaf
        self.parent = parent
        self.level = level

    def __repr__(self):
        return f'IntervalNode(Level={self.level}, IsLeaf={self.is_leaf}, Entries={len(self.entries)})'


# ----------------------------------------------------------------------- #
#                           Interval Tree
# ----------------------------------------------------------------------- #

class IntervalTree:
    def __init__(self):
        self.root = IntervalTreeNode(is_leaf=True, level=0)