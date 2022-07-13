from z3 import *
import json


class ETRSolver:
    def __init__(self, data):
        self.solver = Solver()
        self.path = data.get("path", [])
        self.cycles = data.get("cycles", {})
        self.transitions = []
        for item in self.get_path():
            self.transitions.append(item)
        for cycle in self.get_cycles().values():
            for item in cycle:
                self.transitions.append(item)

    def get_path(self):
        return self.path

    def get_cycles(self):
        return self.cycles

    def get_cycle(self, name):
        return self.cycles[name]

    def get_transitions(self):
        return self.transitions

    def solve(self, target_x, target_y):
        self.solver.reset()
        path_x, path_y = Reals("path_x path_y")
        cycles_x = [Real(f'cycle_x_{name}') for name in self.get_cycles()]
        cycles_y = [Real(f'cycle_y_{name}') for name in self.get_cycles()]
        self.solve_path(path_x, path_y)

        for name, cycle_x, cycle_y in zip(self.get_cycles().keys(), cycles_x, cycles_y):
            self.solve_cycle(name, cycle_x, cycle_y)
        sum_x = Sum([cycle_x for cycle_x in cycles_x])
        sum_y = Sum([cycle_y for cycle_y in cycles_y])

        self.solver.add(path_x + sum_x == target_x, path_y + sum_y == target_y)

        self.solve_negatives()
        if self.solver.check() == sat:
            return self.solver.model()
        else:
            return self.solver.check()  # Todo: raise proper error

    def verify(self):
        return self.solver.check() == sat

    def solve_path(self, path_x, path_y):
        X = [Real(f'x_{item[0]}_{item[3]}') for item in self.get_path()]
        Y = [Real(f'y_{item[0]}_{item[3]}') for item in self.get_path()]
        alpha = [Real(f'a_{item[0]}_{item[3]}') for item in self.get_path()]
        sum_x = Sum([a * x for (a, x) in zip(alpha, X)])
        sum_y = Sum([a * y for (a, y) in zip(alpha, Y)])
        self.solver.add(sum_x == path_x, sum_y == path_y)

        x_s = [Real(item[1]) if isinstance(item[1], str) else item[1] for item in self.get_path()]
        y_s = [Real(item[2]) if isinstance(item[2], str) else item[2] for item in self.get_path()]
        for i in range(len(x_s)):
            self.solver.add(X[i] == x_s[i])
            self.solver.add(Y[i] == y_s[i])
            self.solver.add(alpha[i] > 0, alpha[i] <= 1)

    def all_true(self, l):
        result = True
        for item in l:
            result = And(result, item)
        return result

    def solve_cycle(self, name, cycle_x, cycle_y):
        X = [Real(f'x_{item[0]}_{item[3]}') for item in self.get_cycle(name)]
        Y = [Real(f'y_{item[0]}_{item[3]}') for item in self.get_cycle(name)]
        alpha = [Real(f'a_{item[0]}_{item[3]}') for item in self.get_cycle(name)]
        sum_x = Sum([a * x for (a, x) in zip(alpha, X)])
        sum_y = Sum([a * y for (a, y) in zip(alpha, Y)])
        self.solver.add(Or(And(sum_x == cycle_x, sum_y == cycle_y), And(cycle_x == 0, cycle_y == 0)))

        x_s = [Real(item[1]) if isinstance(item[1], str) else item[1] for item in self.get_cycle(name)]
        y_s = [Real(item[2]) if isinstance(item[2], str) else item[2] for item in self.get_cycle(name)]

        trivial = self.all_true([X[i] * Y[i + 1] == X[i + 1] * Y[i] for i in range(len(X) - 1)])
        for i in range(len(x_s)):
            self.solver.add(X[i] == x_s[i])
            self.solver.add(Y[i] == y_s[i])
            self.solver.add(Or(And(trivial, alpha[i] >= 0), And(Not(trivial), alpha[i] > 0)))

    def solve_negatives(self):
        negatives = set()
        for item in self.get_transitions():
            if isinstance(item[1], str) and item[1][0] == '-':
                negatives.add(item[1])
            if isinstance(item[2], str) and item[2][0] == '-':
                negatives.add(item[2])
        for item in negatives:
            self.solver.add(Real(item) == -Real(item[1:]))
