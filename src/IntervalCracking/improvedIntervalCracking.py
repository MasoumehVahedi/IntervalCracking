"""
    Clarifying the Purpose of Node Splitting and Search-And-Crack:

   1- Node Splitting is about maintaining the overall tree structure and ensuring that
      the tree does not become unbalanced or inefficient due to overfilled nodes.
      It’s a structural operation that’s triggered by the state of the node
      (i.e., when it has too many entries).

   2- Search-and-Crack is about optimizing the querying process by dynamically refining
      the set of intervals to be checked. It’s an operational technique that’s used during
      queries to make them faster and more efficient by cracking intervals based on the query itself.

"""


import math
from collections import deque

from interval_structures import Interval, IntervalTree, IntervalTreeEntry, IntervalTreeNode


class IntervalCracking:
    def __init__(self, intervals=None, max_entries=200, min_entries=None, FIRST_INIT=float("inf"), END_INIT=float("-inf")):
        self.max_entries = max_entries
        self.min_entries = min_entries or math.ceil(max_entries / 2)
        self.FIRST_INIT = FIRST_INIT
        self.END_INIT = END_INIT
        self.tree = IntervalTree()
        if intervals:
            self.bulk_insert(intervals)

    def bulk_insert(self, intervals):
        for interval in intervals:
            self.insert_interval(interval)

    def insert_interval(self, interval):
        #print("Inserting interval:", interval)  # Debugging statement
        node = self.tree.root
        interval_obj = Interval(interval[0][0], interval[0][1])
        while not node.is_leaf:
            node = self.choose_subtree(node, interval_obj)

        node.entries.append(IntervalTreeEntry(interval_obj, interval[1]))

        if len(node.entries) > self.max_entries:
            self.split_node(node)

    def choose_subtree(self, node, interval):
        best_entry = min(
            node.entries,
            key=lambda entry: self.enlargement_needed(entry.interval, interval)
        )
        return best_entry.child

    def enlargement_needed(self, interval1, interval2):
        combined_interval = self.calculate_bounding_interval([IntervalTreeEntry(interval1), IntervalTreeEntry(interval2)])
        return (combined_interval.max_val - combined_interval.min_val) - (interval1.max_val - interval1.min_val)

    def split_node(self, node):
        #print("Splitting node:", node)  # Debugging statement
        entries = node.entries
        node.entries = []
        node.is_leaf = False

        if len(entries) <= self.min_entries:
            left_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            right_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            midpoint = len(entries) // 2
            left_child.entries = entries[:midpoint]
            right_child.entries = entries[midpoint:]
            node.entries.append(IntervalTreeEntry(self.calculate_bounding_interval(left_child.entries), child=left_child))
            node.entries.append(IntervalTreeEntry(self.calculate_bounding_interval(right_child.entries), child=right_child))
        else:
            left_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            right_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            overlap_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)

            left_entries, right_entries, overlap_entries = self.median_split(entries)

            left_child.entries = left_entries
            right_child.entries = right_entries
            overlap_child.entries = overlap_entries

            node.entries.append(IntervalTreeEntry(self.calculate_bounding_interval(left_child.entries), child=left_child))
            node.entries.append(IntervalTreeEntry(self.calculate_bounding_interval(right_child.entries), child=right_child))
            if overlap_entries:
                node.entries.append(
                    IntervalTreeEntry(self.calculate_bounding_interval(overlap_child.entries), child=overlap_child))

    def median_split(self, entries):
        """
           The purpose of median_split is to ensure that the intervals are divided
           as evenly as possible between the left, right, and overlapped nodes to
           maintain tree balance.
        """
        intervals = sorted(entries, key=lambda entry: entry.interval.min_val)
        median_index = len(intervals) // 2
        median_value = intervals[median_index].interval.min_val

        left_entries = [entry for entry in intervals if entry.interval.max_val <= median_value]
        right_entries = [entry for entry in intervals if entry.interval.min_val > median_value]
        overlap_entries = [entry for entry in intervals if entry not in left_entries and entry not in right_entries]

        return left_entries, right_entries, overlap_entries

    def intervals_overlap(self, interval1, interval2):
        return not (interval1.max_val < interval2.min_val or interval1.min_val > interval2.max_val)

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

    def searchAndCrack(self, query_interval, query, node):
        xmin, ymin, xmax, ymax = query
        query_results = []

        self.local_intervals = [(entry.interval, entry.data) for entry in node.entries]

        if len(node.entries) <= self.max_entries:
            query_results.extend(
                [entry.data for entry in node.entries if
                 (entry.data[2] > xmin and entry.data[0] < xmax and entry.data[3] > ymin and entry.data[1] < ymax)])
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

        right_intervals = self.local_intervals[crack_index_min:crack_index_max]
        overlapped_intervals = self.local_intervals[crack_index_min:crack_index_max]

        node.entries.clear()

        if left_intervals:
            left_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            left_child.entries = [IntervalTreeEntry(interval, data=data) for interval, data in left_intervals]
            left_bounding_interval = self.calculate_bounding_interval(left_child.entries)
            node.is_leaf = False
            node.entries.append(IntervalTreeEntry(left_bounding_interval, child=left_child))

        if right_intervals:
            right_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            right_child.entries = [IntervalTreeEntry(interval, data=data) for interval, data in right_intervals]
            right_bounding_interval = self.calculate_bounding_interval(right_child.entries)
            node.is_leaf = False
            node.entries.append(IntervalTreeEntry(right_bounding_interval, child=right_child))

        if overlapped_intervals:
            overlapped_child = IntervalTreeNode(is_leaf=True, parent=node, level=node.level + 1)
            overlapped_child.entries = [IntervalTreeEntry(interval, data=data) for interval, data in overlapped_intervals]
            overlapped_bounding_interval = self.calculate_bounding_interval(overlapped_child.entries)
            node.is_leaf = False
            node.entries.append(IntervalTreeEntry(overlapped_bounding_interval, child=overlapped_child))

        for entry in overlapped_intervals:
            mbr = entry[1]
            if mbr[2] > xmin and mbr[0] < xmax and mbr[3] > ymin and mbr[1] < ymax:
                query_results.append(mbr)

        return query_results

    def crackOnAxisMin(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        return self.partition(intervals, low, high, crack_value, left_rect, right_rect, check_min)

    def crackOnAxisMax(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        return self.partition(intervals, low, high, crack_value, left_rect, right_rect, check_min)

    def partition(self, intervals, low, high, crack_value, left_rect, right_rect, check_min):
        x1, x2 = low, high - 1

        while x1 <= x2:
            interval = intervals[x1][0]
            if check_min:
                if interval.max_val < crack_value:
                    if interval.min_val < left_rect.min_val:
                        left_rect.min_val = interval.min_val
                    if interval.max_val > left_rect.max_val:
                        left_rect.max_val = interval.max_val
                    x1 += 1
                elif interval.min_val > crack_value:
                    if interval.min_val < right_rect.min_val:
                        right_rect.min_val = interval.min_val
                    if interval.max_val > right_rect.max_val:
                        right_rect.max_val = interval.max_val
                    intervals[x1], intervals[x2] = intervals[x2], intervals[x1]
                    x2 -= 1
                else:
                    # Move to overlap section
                    x1 += 1
            else:
                if interval.min_val > crack_value:
                    if interval.min_val < right_rect.min_val:
                        right_rect.min_val = interval.min_val
                    if interval.max_val > right_rect.max_val:
                        right_rect.max_val = interval.max_val
                    x1 += 1
                elif interval.max_val < crack_value:
                    if interval.min_val < left_rect.min_val:
                        left_rect.min_val = interval.min_val
                    if interval.max_val > left_rect.max_val:
                        left_rect.max_val = interval.max_val
                    intervals[x1], intervals[x2] = intervals[x2], intervals[x1]
                    x2 -= 1
                else:
                    x1 += 1
        return x1

    def calculate_bounding_interval(self, intervals):
        if not intervals:
            return Interval(self.FIRST_INIT, self.END_INIT)

        min_val = min(entry.interval.min_val for entry in intervals)
        max_val = max(entry.interval.max_val for entry in intervals)
        return Interval(min_val, max_val)


def visualize_tree(node, level=0):
    indent = " " * (4 * level)
    node_type = "Leaf" if node.is_leaf else "Internal"
    print(f"{indent}Level {level}, {node_type}, Entries: {len(node.entries)}")

    if not node.is_leaf:
        for i, entry in enumerate(node.entries):
            child_type = ""
            if i == 0:
                child_type = "Left"
            elif i == 1 and len(node.entries) == 3:
                child_type = "Overlapped"
            else:
                child_type = "Right"

            print(f"{indent}  -> Child Type: {child_type}")
            visualize_tree(entry.child, level + 1)


