from ETRSolver import ETRSolver
import unittest


class TestETRSolver(unittest.TestCase):
    def test_basic_path(self):
        data = {"path": [
            [0, 1, 1, 1],
            [1, 2, 2, 2],
            [2, -1, 0, 3],
            [3, 3, -5, 4],
            [4, 2, 6, 5],
            [5, 1, 0, 6],
            [6, 0, -2, 7]]}
        etr = ETRSolver(data)
        X = range(8)
        Y = range(8)
        for x, y in zip(X, Y):
            etr.solve(x, y)
            self.assertTrue(etr.verify())

    def test_basic_cycle(self):
        data = {"cycles": {"c1": [
            [0, 1, 1, 1],
            [1, 1, 0, 0]]}}
        etr = ETRSolver(data)
        etr.solve(2, 2)
        self.assertFalse(etr.verify())
        etr.solve(10, 0)
        self.assertFalse(etr.verify())
        etr.solve(0, 0)
        self.assertTrue(etr.verify())
        etr.solve(2, 1)
        self.assertTrue(etr.verify())

    def test_multiple_cycles(self):
        data = {"path": [[0, 0, 0, 2]],
                "cycles": {
                    "c1": [
                        [0, 1, 1, 1],
                        [1, 1, 0, 0]],
                    "c2": [
                        [2, 0, 1, 3],
                        [3, 2, 2, 2]]}}

        etr = ETRSolver(data)
        etr.solve(2, 1)
        self.assertTrue(etr.verify())
        etr.solve(2, 2)
        self.assertTrue(etr.verify())
        etr.solve(10, 0)
        self.assertFalse(etr.verify())

    def test_path_variables(self):
        data = {"path": [
            [0, "X", 10, 1],
            [1, "-X", 2, 2]]}
        etr = ETRSolver(data)
        etr.solve(0, 12)
        self.assertTrue(etr.verify())
        for i in range(1, 20):
            etr.solve(i, 12)
            self.assertFalse(etr.verify())
            etr.solve(i, 11.9)
            self.assertTrue(etr.verify())

    def test_cycle_variables(self):
        data = {"cycles": {"c1": [
            [0, "X", 1, 1],
            [1, -1, 2, 0]]}}
        etr = ETRSolver(data)
        for i in range(-10, 10):
            etr.solve(i, -5)
            self.assertFalse(etr.verify())
            etr.solve(i, 20)
            self.assertTrue(etr.verify())


