from ETRSolver import ETRSolver
from VASS import VASS
import json


def main():
    # with open('example.json', 'r') as f:
    #     data = json.load(f)
    # etr = ETRSolver(data)
    # print(etr.solve(3, -1))
    #
    # with open('basic_path.json', 'r') as f:
    #     data = json.load(f)
    # etr = ETRSolver(data)
    # print(etr.solve(0, 0))
    # etr = ETRSolver(data)
    # print(etr.solve(1, 1))
    with open('vass.json', 'r') as f:
        data = json.load(f)
    vass = VASS(data)
    # print(vass.get_states())
    # print(vass.adjacency_list())
    # vass.construct_reachability_tree()
    print(vass.linear_path_scheme())


if __name__ == '__main__':
    main()
