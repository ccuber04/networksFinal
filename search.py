"""Generic library for solving search problems"""

import math
from pq import PriorityQueue
from collections import deque

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent  # from where we came
        self.action = action  # action that brought us here
        self.path_cost = path_cost  # from initial state to current node

    def __len__(self):
        if self.parent is None:
            return 0
        else:
            return len(self.parent) + 1

    def __repr__(self):
        return f"Node({self.state})"

    def __lt__(self, other):
        """Node a < Node b"""
        return self.path_cost < other.path_cost

failure = Node('failure', path_cost=math.inf)
cutoff = Node('cutoff', path_cost=math.inf)

def path_actions(node):
    """Returns the list of actions that brought us here to this node"""
    actions = []
    while node.parent is not None:
        actions.append(node.action)
        node = node.parent
    actions.reverse()
    return actions

def path_states(node):
    """Returns a list of states that we passed through to get
    to this node"""
    states = []
    while node.parent is not None:
        states.append(node.state)
        node = node.parent
    states.reverse()
    return states

class Problem:
    def __init__(self, initial, is_goal, result, actions, action_cost):
        self.initial = initial  # starting node state
        self.is_goal = is_goal  # function for determining if node is goal(s)
        self.result = result    # function(state, action) -> action
        self.actions = actions  # function(state) -> [actions]
        self.action_cost = action_cost  # function(state, action, new_state) -> cost

def expand(problem, node):
    """Given problem and current node, expand the frontier from node.
    Return a list of nodes."""
    # 1. figure out what actions I can take
    state = node.state
    for action in problem.actions(state):
        # 2. simulate those actions -> new states
        new_state = problem.result(state, action)

        # 3. calculate an accumulated cost to each new node
        cost = node.path_cost + problem.action_cost(state, action, new_state)
        yield Node(state=new_state, parent=node, action=action, path_cost=cost)

def g(n):
    return n.path_cost

def best_first_search(problem, f):
    """Search path by choosing Node that minimizes f(node)"""
    node = Node(problem.initial)
    frontier = PriorityQueue([node], f)
    reached = {problem.initial: node}

    while not frontier.empty():
        node = frontier.pop()
        if problem.is_goal(node.state):
            print("best_first_search: reached = {}".format(len(reached)))
            print("best_first_search: path length = {}".format(len(path_actions(node))))
            return node

        for child in expand(problem, node):
            s = child.state
            # child is new, or path to it is shorter than previously seen
            if s not in reached or child.path_cost < reached[s].path_cost:
                reached[s] = child
                frontier.add(child)
    return failure

def breadth_first_search(problem):
    """Search path by choosing the fewest actions"""
    node = Node(problem.initial)
    if problem.is_goal(node.state):
        return node
    frontier = deque([node])
    reached = {problem.initial}

    while len(frontier) != 0:
        node = frontier.pop()
        for child in expand(problem, node):
            s = child.state
            if problem.is_goal(s):
                print("breadth_first_search: reached = {}".format(len(reached)))
                print("breadth_first_search: path length = {}".format(len(path_actions(child))))
                return child
            if s not in reached:
                reached.add(s)
                frontier.appendleft(child)
    return failure

def uniform_cost_search(problem):
    """Search path by prioritizing the path cost"""
    print("uniform_cost_search:")
    return best_first_search(problem, f=g)

def depth_first(problem):
    """Search the deepest nodes in the tree first"""
    print("depth_first:")
    return best_first_search(problem, f=lambda n: -len(n))

def astar_search(problem, h):
    """Search by adding a heuristic to the nodes' path cost"""
    print("astar_search:")
    return best_first_search(problem, f=lambda n: g(n) + h(n))

def astar_weighted_search(problem, h, w):
    """Search by adding a weighted heuristic to the nodes' path cost"""
    print("astar_weighted_search:")
    return best_first_search(problem, f=lambda n: g(n) + w*h(n))

def greedy_search(problem, h):
    """Search nodes with minimum h(n)"""
    print("greedy_search:")
    return best_first_search(problem, f=h)
