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
        # ret = "|" * level + repr(self.node) + "\n"
        # for child in self.children:
        #     ret += child.__str__(level + 1)
        # return ret
        ret = repr(self.node) + " "
        for child in self.children:
            ret += child.__str__()
        return ret

    def __repr__(self):
        return str(self.node)


class VASS:
    def __init__(self, data):
        self.start = data.get("start")
        self.end = data.get("end")
        self.init_x = data.get("start_x")
        self.init_y = data.get("start_y")
        self.target_x = data.get("end_x")
        self.target_y = data.get("end_x")
        self.edges = data.get("edges", [])

    def get_states(self):
        states = set()
        for item in self.edges:
            states.add(item["p"])
            states.add(item["q"])
        return list(states)

    def adjacency_list(self):
        adj_list = defaultdict(list)
        for item in self.edges:
            adj_list[item["p"]].append(item["q"])
            adj_list[item["p"]] = sorted(adj_list[item["p"]])
        return dict(adj_list)

    def get_transition(self, p: str, q: str):
        for item in self.edges:
            if str(item["p"]) == p and str(item["q"]) == q:
                return item["x"], item["y"]
        print(p, q)

    def construct_reachability_tree(self):
        tree = Tree(self.start)
        adj_list = self.adjacency_list()
        self.const_tree_rec(tree, adj_list)
        return tree

    def const_tree_rec(self, tree, adj_list, depth=0):
        if depth > 2 * len(self.edges) * len(self.get_states()):
            return
        if tree.node == self.end:
            return
        for item in adj_list[tree.node]:
            new_tree = Tree(item, parent=tree)
            tree.add_child(new_tree)
            if item not in tree.get_parents():
                self.const_tree_rec(new_tree, adj_list, depth + 1)

    def linear_path_scheme(self):
        tree = self.construct_reachability_tree()
        paths = list()
        cycles = list()

        stack = list()
        preorder = list()
        preorder.append(tree.node)
        stack.append(tree)
        while len(stack) > 0:
            flag = 0
            if not stack[-1].children:
                stack.pop()
            else:
                par = stack[-1]
                for child in par.children:
                    if child not in preorder:
                        stack.append(child)
                        preorder.append(child)
                        if child.node == self.end:
                            paths.append(list(reversed([child.node] + child.get_parents())))
                        if child.node in child.get_parents():
                            cycle = list()
                            cycle.insert(0, child.node)
                            for item in child.get_parents():
                                cycle.insert(0, item)
                                if item == child.node:
                                    break
                            cycles.append(cycle)
                            break
                        flag = 1
                        break
                if flag == 0:
                    stack.pop()
        print(cycles)
        print(paths)
        lpss = list()
        for path in paths:
            visited = list()
            to_flatten = list()
            path_extend = list()
            basic_cycles = list()
            for cycle in cycles:
                if cycle[0] not in path:
                    to_flatten.append(cycle)
                else:
                    basic_cycles.append(cycle)
                    if cycle[0] not in visited:
                        visited.append(cycle[0])
                    else:
                        path_extend.append(cycle[0])
            for item in path_extend:
                path.insert(path.index(item), item)
            lpss.append(self.export_lps(path, basic_cycles))

            for cycle in to_flatten:
                for other_cycle in basic_cycles:
                    if cycle[0] in other_cycle:
                        path[path.index(other_cycle[0]) + 1:path.index(other_cycle[0]) + 1] = other_cycle[1:]
                        lpss.append(self.export_lps(path, basic_cycles + [cycle]))
        return lpss

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
