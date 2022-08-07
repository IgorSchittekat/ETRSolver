import json
from collections import defaultdict
import numpy as np


class Tree:
    def __init__(self, node, parent=None):
        self.parent = parent
        self.children = list()
        self.node = node

    def add_child(self, node):
        self.children.append(node)

    def get_parents(self):
        parent = self.parent
        parents = list()
        while parent is not None:
            parents.append(parent.node)
            parent = parent.parent
        return parents

    def __str__(self, level=0):
        ret = repr(self.node) + " "
        for child in self.children:
            ret += child.__str__()
        return ret

    def __repr__(self):
        return str(self.node)


class VASS:
    """
    This function initializes all class variables. The states are all converted to strings.
    If multiple transitions exist between two states, a new state is created as intermediate state for
    all except one of the transitions. The update to this transition will always be (0, 0).
    This to have no two states with more than one transition.
    :param data: json object with all info
        start: the starting state in the VASS
        end: the target state in the VASS
        start_x: initial value of x
        start_y: initial value of y
        end_x: the target value of x
        end_y: the target value of y
        edges: a list containing json objects, where each object has:
            p: the state from where the transition starts
            q: the state where the transition ends
            x: the update value for x
            y: the update value for y
    """
    def __init__(self, data):
        self.start = str(data.get("start"))
        self.end = str(data.get("end"))
        self.init_x = data.get("start_x")
        self.init_y = data.get("start_y")
        self.target_x = data.get("end_x")
        self.target_y = data.get("end_x")
        self.edges = []
        edges = data.get("edges", [])
        states = self.get_states(edges)
        edge_ctr = np.zeros(len(states), dtype=int)
        for edge in edges:
            p = str(edge["p"])
            q = str(edge["q"])
            x = edge["x"]
            y = edge["y"]
            if self.edge_exists(p, q):
                new_state = f'{p}-{edge_ctr[states.index(edge["p"])]}'
                edge_ctr[states.index(edge["p"])] += 1
                self.edges.append({"p": p, "x": 0, "y": 0, "q": new_state})
                self.edges.append({"p": new_state, "x": x, "y": y, "q": q})
            else:
                self.edges.append({"p": p, "x": x, "y": y, "q": q})

    """
    :param p: the state where the transition would start
    :type p: str
    :param q: the state where the transition would end
    :type q: str
    :returns: a boolean representing whether or not a transition exists between p and q
    :rtype: bool
    """
    def edge_exists(self, p: str, q: str) -> bool:
        for edge in self.edges:
            if edge["p"] == p and edge["q"] == q:
                return True
        return False

    """
    :param edges: The list of all edges. If None, self.edges is used. 
    :returns: all the states within the VASS
    """
    def get_states(self, edges=None):
        if edges is None:
            edges = self.edges
        states = set()
        for item in edges:
            states.add(item["p"])
            states.add(item["q"])
        return list(states)

    """
    :returns: the sorted adjacency list for each state
    """
    def adjacency_list(self):
        adj_list = defaultdict(list)
        for item in self.edges:
            adj_list[item["p"]].append(item["q"])
            adj_list[item["p"]] = sorted(adj_list[item["p"]])
        return adj_list

    """
    :param p: the state where the transition would start
    :type p: str
    :param q: the state where the transition would end
    :type q: str
    :returns: the values for x and y in the transition
    :exception: If no transition exists between p and q
    """
    def get_transition(self, p: str, q: str):
        for item in self.edges:
            if item["p"] == p and item["q"] == q:
                return item["x"], item["y"]
        raise IndexError(f"Transition not found between state {p} and {q}.")

    """
    This function creates an adjacency tree starting in self.start, and uses 
    self.const_tree_rec() to recursively create the tree
    :returns: the adjacency tree
    """
    def construct_reachability_tree(self):
        tree = Tree(self.start)
        adj_list = self.adjacency_list()
        self.const_tree_rec(tree, adj_list)
        return tree

    """
    This function recursively constructs a tree, until all new children are already in the list of parents. 
    :param tree: the tree as the parent, to create new children for
    :param adj_list: the adjacency list to search for all children
    :param depth: to give the depth of the tree
    """
    def const_tree_rec(self, tree, adj_list, depth=0):
        for item in adj_list[tree.node]:
            new_tree = Tree(item, parent=tree)
            tree.add_child(new_tree)
            if item not in tree.get_parents():
                self.const_tree_rec(new_tree, adj_list, depth + 1)
    """
    Rotate the cycle, such that the given state becomes the start and end state. 
    If the given state is not in the cycle, or the given state is already the start and end state, do nothing.
    :param cycle: Cycle to rotate
    :param start: New start and end state for the cycle
    :returns: The rotated cycle, or the same cycle is the given state is not in the cycle
    """
    def rotate_cycle(self, cycle, start):
        if start not in cycle or cycle[0] == start:
            return cycle
        idx = cycle.index(start)
        return cycle[idx:] + cycle[1:idx] + [start]

    """
    Check if a cycle already exists in a given list of cycles. If a rotation of the cycle exists, the cycle exists.
    :param cycles: List of all cycles to check
    :param new_cycle: cycle to check if it exists in the list
    :returns: Boolean whether the cycle exists in the list or not
    :rtype: bool
    """
    def cycle_exists(self, cycles, new_cycle):
        filtered = filter(lambda x: len(x) == len(new_cycle), cycles)
        for cycle in filtered:
            if len(set(cycle) & set(new_cycle)) == len(set(new_cycle)):
                if self.rotate_cycle(cycle, new_cycle[0]) == new_cycle:
                    return True
        return False

    """
    Find all paths and cycles for the linear path schemes.
    The reachability tree is iteratively traversed using preorder traversal.
    If self.end is found, the path from the start to this state is added to all paths. 
    If a state is found that also appears in the list of it's parents, a cycle is found, and this cycle is added to 
    the list of all cycles, if this cycle is not already in the list.
    :returns: a list containing all different paths from self.start to self.end, and a list of all cycles within 
    the VASS that can be reached from self.start.
    """
    def find_paths_and_cycles(self):
        tree = self.construct_reachability_tree()
        paths = list()
        cycles = list()

        stack = list()
        preorder = list()
        preorder.append(tree.node)
        stack.append(tree)
        while len(stack) > 0:
            flag = False
            if not stack[-1].children:
                stack.pop()
            else:
                par = stack[-1]
                for child in par.children:
                    if child not in preorder:
                        stack.append(child)
                        preorder.append(child)
                        if child.node == self.end:
                            if child.node not in child.get_parents():
                                paths.append(list(reversed([child.node] + child.get_parents())))
                        if child.node in child.get_parents():
                            cycle = list()
                            cycle.insert(0, child.node)
                            for item in child.get_parents():
                                cycle.insert(0, item)
                                if item == child.node:
                                    break
                            if not self.cycle_exists(cycles, cycle):
                                cycles.append(cycle)
                            break
                        flag = True
                        break
                if not flag:
                    stack.pop()
        return paths, cycles

    """
    Constructs a list of linear path schemes that cove all possible solutions.
    For each path from self.start to self.end:
        If the start of the cycle is a state in the path, the cycle can be added to the lps. 
        If more than one cycle starts in the same state, a copy of this state is made in the path, and 
        linked to this state with transition (0, 0), from which the path continuous. 
        For all cycles that do not have a state on the path, we look for earlier added cycles that
        have a state in these cycles, and we flatten these cycles and add them to the path. 
        For each of these newly flattened cycles, we create a separate lps. 
        This is repeated until all cycles are added to a lps, or no more cycles can be added.
        :returns: a list of linear path schemes. 
    """
    def linear_path_scheme(self):
        paths, cycles = self.find_paths_and_cycles()
        print("paths", len(paths))
        print("cycles", len(cycles))
        lpss = list()
        for path in paths:
            # print(path)
            visited = list()
            to_flatten = list()
            basic_cycles = list()
            for cycle in cycles:
                flag = True
                if cycle[0] not in path:
                    intersection = list(set(cycle) & set(path))
                    if intersection:
                        cycle = self.rotate_cycle(cycle, intersection[0])
                    else:
                        flag = False
                        if cycle not in to_flatten:
                            to_flatten.append(cycle)
                if flag:
                    basic_cycles.append(cycle)
                    if cycle[0] not in visited:
                        visited.append(cycle[0])
                    else:
                        path.insert(path.index(cycle[0]), cycle[0])
            lpss.append(self.export_lps(path, basic_cycles))

            while to_flatten:
                added_cycles = sorted(basic_cycles, key=len, reverse=True)
                all_states = set([j for i in to_flatten for j in i])
                cycle_to_flatten = None
                for added_cycle in added_cycles:
                    intersection = list(set(added_cycle) & all_states)
                    if intersection:
                        cycle_to_flatten = added_cycle
                        break
                if cycle_to_flatten is None:
                    break
                path[path.index(cycle_to_flatten[0]) + 1:path.index(cycle_to_flatten[0]) + 1] = cycle_to_flatten[1:]
                visited = list()
                to_remove = list()
                for cycle in to_flatten:
                    intersection = list(set(cycle) & set(path))
                    if intersection:
                        to_remove.append(cycle)
                        cycle = self.rotate_cycle(cycle, intersection[0])
                        basic_cycles.append(cycle)
                        if cycle[0] not in visited:
                            visited.append(cycle[0])
                        else:
                            path.insert(path.index(cycle[0]), cycle[0])
                lpss.append(self.export_lps(path, basic_cycles))
                for cycle in to_remove:
                    to_flatten.remove(cycle)
        return lpss

    """
    Label all states in the lps uniquely, in a way that there is at most one cycle on each state in the path, 
    and there are no cycles starting on cycles. 
    :param path: the list of the path in the lps (can contain duplicate labels)
    :param cycles: the list of all cycles in the lps (can contain duplicate labels)
    :returns: paths and cycles where labels are renamed to have no duplicates. 
    """
    def label_unique(self, path, cycles):
        states = self.get_states()
        unique_ctr = np.zeros(len(states), dtype=int)

        new_path = list()
        for item in path:
            new_item = f"{item}_{unique_ctr[states.index(item)]}"
            unique_ctr[states.index(item)] += 1
            new_path.append(new_item)

        unique_ctr_cycle = np.zeros(len(states), dtype=int)
        new_cycles = list()
        for cycle in cycles:
            new_cycle = list()
            for i, item in enumerate(cycle):
                if i == 0 or i == len(cycle) - 1:
                    new_item = f"{item}_{unique_ctr_cycle[states.index(item)]}"
                    new_cycle.append(new_item)
                    if i == len(cycle) - 1:
                        unique_ctr_cycle[states.index(item)] += 1
                else:
                    new_item = f"{item}_{unique_ctr[states.index(item)]}"
                    unique_ctr[states.index(item)] += 1
                    new_cycle.append(new_item)
            new_cycles.append(new_cycle)
        return new_path, new_cycles

    """
    Exports the lps to the format that can be read by the ETRSolver:
        path: a list of transitions, where each of these transitions have 4 elements: 
            the start state of the transition, 
            the update value for x, 
            the update value for y, 
            the end state of the transition
        cycles: a dictionary, where each cycle has a unique name and points to a list of transitions, 
        which have the same elements as within the path.
    :param path: the list of the path in the lps (can contain duplicate labels)
    :param cycles: the list of all cycles in the lps (can contain duplicate labels)
    :returns: the lps in json format
    """
    def export_lps(self, path, cycles):
        path, cycles = self.label_unique(path, cycles)
        data = dict()
        data["path"] = list()
        data["cycles"] = dict()
        for i in range(len(path) - 1):
            p = path[i]
            q = path[i + 1]
            orig_p = p[:p.rfind('_')]
            orig_q = q[:q.rfind('_')]
            if orig_p == orig_q:
                x, y = (0, 0)
            else:
                x, y = self.get_transition(orig_p, orig_q)
            data["path"].append([p, x, y, q])
        counter = 0
        for cycle in cycles:
            counter += 1
            data["cycles"][f"c{counter}"] = list()
            for i in range(len(cycle) - 1):
                p = cycle[i]
                q = cycle[i + 1]
                orig_p = p[:p.rfind('_')]
                orig_q = q[:q.rfind('_')]
                x, y = self.get_transition(orig_p, orig_q)
                data["cycles"][f"c{counter}"].append([p, x, y, q])
        return data
