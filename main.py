from ETRSolver import ETRSolver
import json


def main():
    with open('example.json', 'r') as f:
        data = json.load(f)
    etr = ETRSolver(data)
    print(etr.solve(3, -1))

    with open('basic_path.json', 'r') as f:
        data = json.load(f)
    etr = ETRSolver(data)
    print(etr.solve(0, 0))
    etr = ETRSolver(data)
    print(etr.solve(1, 1))


if __name__ == '__main__':
    main()
