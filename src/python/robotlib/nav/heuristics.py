import numpy as np

from robotlib.nav import PathNode


def euclidean_heuristic(start: PathNode, end: PathNode) -> float:
    return (np.sum(np.subtract(start, end) ** 2)) ** 0.5


def manhattan_heuristic(start: PathNode, end: PathNode) -> float:
    return np.sum(np.abs(np.subtract(start, end)))
