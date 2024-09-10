import math
from collections import deque

class Interval:
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val

    def __repr__(self):
        return f'[{self.min_val}, {self.max_val}]'


class RTreeEntry:
    def __init__(self, interval, data=None, child=None):
        self.interval = interval
        self.data = data
        self.child = child

    def __repr__(self):
        return f'RTreeEntry({self.interval})'


class RTreeNode:
    def __init__(self, is_leaf=True, parent=None, level=0):
        self.entries = []
        self.is_leaf = is_leaf
        self.parent = parent
        self.level = level

    def __repr__(self):
        return f'RTreeNode(Level={self.level}, IsLeaf={self.is_leaf}, Entries={len(self.entries)})'

class RTree:
    def __init__(self):
        self.root = RTreeNode(is_leaf=True, level=0)



class AdaptiveSPLindex:
    def __init__(self, intervals=None, max_entries=128, min_entries=None, FIRST_INIT=None, END_INIT=None):
        self.max_entries = max_entries
        self.min_entries = min_entries or math.ceil(max_entries / 2)
        self.FIRST_INIT = FIRST_INIT
        self.END_INIT = END_INIT
        self.tree = RTree()
        root_node = self.tree.root

        # Create a root node that includes all intervals as the initial tree structure
        overall_interval = self.calculate_bounding_interval([(Interval(interval[0][0], interval[0][1]), interval[1]) for interval in intervals])
        root_node.entries.append(RTreeEntry(overall_interval))
        root_node.is_leaf = False

        # Create the first level of children nodes containing the intervals
        initial_node = RTreeNode(is_leaf=True, parent=root_node, level=1)
        initial_node.entries = [RTreeEntry(Interval(interval[0][0], interval[0][1]), interval[1]) for interval in intervals]
        root_node.entries[0].child = initial_node


    def adaptiveSearch(self, query_interval, query):
        queue = deque([self.tree.root])
        query_results = []

        while queue:
            node = queue.popleft()

            if node.is_leaf:
                results = self.searchAndCrack(query_interval, query, node)
                if results:
                    query_results.extend(results)
            else:
                for entry in node.entries:
                    if entry.child and self.intervals_overlap(entry.interval, query_interval):
                        queue.append(entry.child)

        return query_results
        
    def searchAndCrack(self, query_interval, node):
        query_results = []

        self.local_intervals = [(entry.interval, entry.data) for entry in node.entries]

        if len(node.entries) <= self.max_entries:
            query_results.extend(
                [entry.data for entry in node.entries])
            return query_results

        this_piece_left = 0
        this_piece_right = len(self.local_intervals)

        crack_index_min = self.crackOnAxisMax(self.local_intervals, this_piece_left, this_piece_right,
                                              query_interval.min_val, Interval(self.FIRST_INIT, self.END_INIT),
                                              Interval(self.FIRST_INIT, self.END_INIT), False)

        left_intervals = self.local_intervals[:crack_index_min]

        crack_index_max = self.crackOnAxisMin(self.local_intervals, crack_index_min, this_piece_right,
                                              query_interval.max_val, Interval(self.FIRST_INIT, self.END_INIT),
                                              Interval(self.FIRST_INIT, self.END_INIT), True)

        right_intervals = self.local_intervals[crack_index_max:]
        #print("right_intervals = ", right_intervals)

        overlapped_intervals = self.local_intervals[crack_index_min:crack_index_max]
        #print("overlapped_intervals = ", overlapped_intervals)

        node.entries.clear()  # Clearing the current node entries

        if left_intervals:
            left_child = RTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            left_child.entries = [RTreeEntry(interval, data=data) for interval, data in left_intervals]
            left_bounding_interval = self.calculate_bounding_interval(left_intervals)
            node.is_leaf = False
            node.entries.append(RTreeEntry(left_bounding_interval, child=left_child))

        if right_intervals:
            right_child = RTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            right_child.entries = [RTreeEntry(interval, data=data) for interval, data in right_intervals]
            right_bounding_interval = self.calculate_bounding_interval(right_intervals)
            node.is_leaf = False
            node.entries.append(RTreeEntry(right_bounding_interval, child=right_child))

        if overlapped_intervals:
            overlapped_child = RTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            overlapped_child.entries = [RTreeEntry(interval, data=data) for interval, data in overlapped_intervals]
            overlapped_bounding_interval = self.calculate_bounding_interval(overlapped_intervals)
            node.is_leaf = False
            node.entries.append(RTreeEntry(overlapped_bounding_interval, child=overlapped_child))

        return [entry for entry in overlapped_intervals]

    def calculate_bounding_interval(self, intervals):
        min_val = min(interval[0].min_val for interval in intervals)
        max_val = max(interval[0].max_val for interval in intervals)
        return Interval(min_val, max_val)

    def intervals_overlap(self, interval1, interval2):
        return not (interval1.max_val < interval2.min_val or interval1.min_val > interval2.max_val)

    def crackOnAxisMin(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        return self.partition(intervals, low, high, crack_value, left_rect, right_rect, check_min)

    def crackOnAxisMax(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        return self.partition(intervals, low, high, crack_value, left_rect, right_rect, check_min)

    def partition(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        x1, x2 = low, high - 1

        if check_min:
            while x1 <= x2:
                if intervals[x1][0].min_val < crack_value:
                    if intervals[x1][0].max_val > left_rect.max_val:
                        left_rect.max_val = intervals[x1][0].max_val
                    x1 += 1
                else:
                    while x2 >= x1 and intervals[x2][0].min_val >= crack_value:
                        if intervals[x2][0].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2][0].min_val
                        if intervals[x2][0].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2][0].max_val
                        x2 -= 1

                    if x1 < x2:
                        intervals[x1], intervals[x2] = intervals[x2], intervals[x1]
                        if intervals[x1][0].max_val > left_rect.max_val:
                            left_rect.max_val = intervals[x1][0].max_val
                        if intervals[x2][0].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2][0].min_val
                        if intervals[x2][0].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2][0].max_val
                        x2 -= 1
                        x1 += 1
        else:
            while x1 <= x2:
                if intervals[x1][0].max_val < crack_value:
                    if intervals[x1][0].min_val < left_rect.min_val:
                        left_rect.min_val = intervals[x1][0].min_val
                    if intervals[x1][0].max_val > left_rect.max_val:
                        left_rect.max_val = intervals[x1][0].max_val
                    x1 += 1
                else:
                    while x2 >= x1 and intervals[x2][0].max_val >= crack_value:
                        if intervals[x2][0].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2][0].min_val
                        if intervals[x2][0].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2][0].max_val
                        x2 -= 1

                    if x1 < x2:
                        intervals[x1], intervals[x2] = intervals[x2], intervals[x1]
                        if intervals[x1][0].min_val < left_rect.min_val:
                            left_rect.min_val = intervals[x1][0].min_val
                        if intervals[x1][0].max_val > left_rect.max_val:
                            left_rect.max_val = intervals[x1][0].max_val
                        if intervals[x2][0].min_val < right_rect.min_val:
                            right_rect.min_val = intervals[x2][0].min_val
                        if intervals[x2][0].max_val > right_rect.max_val:
                            right_rect.max_val = intervals[x2][0].max_val
                        x2 -= 1
                        x1 += 1
        return x1


    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.tree.root

        result = []
        queue = deque([(node, level)])

        while queue:
            node, level = queue.popleft()
            for entry in node.entries:
                if entry.child:
                    result.append(' ' * 4 * level + f'Node {level}: Interval = {entry.interval}')
                    queue.append((entry.child, level + 1))
                else:
                    result.append(' ' * 4 * level + f'Leaf {level + 1}: {entry.interval}')
        return result