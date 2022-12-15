import numpy as np
from collections import defaultdict

import reversi as rev
import greedy_base as gb

from tqdm import tqdm

from time import perf_counter

from copy import deepcopy

class MonteCarloTreeSearchNode():
    def __init__(self, state, player=True, parent=None, parent_action=None,tile=None):
        self.state = state
        self.parent = parent
        self.tile = tile
        self.player = player
        self.passes = 0
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions(state,tile)
        # print('-----------------MOSTRAR-NOVO----------------------')
        # rev.drawBoard(state)s
        # print(self._untried_actions)
        # print('--------------FI,-NOVO-------------')
        return

    def untried_actions(self,state,tile):
        if self.player:
            self._untried_actions = self.get_legal_actions(state,tile)
        else:
            self._untried_actions = []
        return self._untried_actions

    def update_passes(self,passes):
        self.passes = passes

    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses

    def n(self):
        return self._number_of_visits

    def expand(self):
        # print(self._untried_actions)
        x,y = self._untried_actions.pop()
        # print('prior expansion')
        # rev.drawBoard(self.state)
        # print('post exp')
        next_state = self.move(deepcopy(self.state),deepcopy(self.tile),x,y)
        child_node = MonteCarloTreeSearchNode(next_state,player=self.player,tile=self.tile, parent=self, parent_action=(x,y))
        self.children.append(child_node)
        return child_node 

    def is_terminal_node(self):
        return self.is_game_over()

    def rollout(self):
        current_rollout_state = deepcopy(self.state)
        pt = self.tile
        et = 'X' if pt == 'O' else 'O'
        while not self.is_game_over():
            if self.player:
                nowtile = pt
            else:
                nowtile = et
            # possible_moves = self.get_legal_actions(current_rollout_state,nowtile)
            # # print(possible_moves)
            ac = gb.chooseGreedyMove(current_rollout_state,nowtile)
            if ac is None:
                self.player = not self.player
                self.passes += 1
                continue
            self.passes = 0
            x,y = ac
            
            # if not possible_moves:
            #     self.player = not self.player
            #     continue
            # x,y = self.rollout_policy(possible_moves)
            
            current_rollout_state = self.move(current_rollout_state,nowtile,x,y)
            # self.player = not self.player
        return self.game_result(current_rollout_state)

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        # print('len de untried ',self._untried_actions,' len: ',len(self._untried_actions))
        return len(self._untried_actions) == 0

    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]

    def _tree_policy(self):
        # current_node = self
        # print('in tree, show child: ',self.children)
        while not self.is_terminal_node():
            if not self.is_fully_expanded():
                return self.expand()
            else:
                return self.best_child()
        return self.best_child()

    def best_action(self):
        simulation_no = 300
        # while len(self._untried_actions) > 0:
        # print(self.get_legal_actions(self.state,self.tile))
        if not self.get_legal_actions(self.state,self.tile):
            return 'pass'
        # for _ in (range(simulation_no)):
        t = perf_counter()
        while (perf_counter() - t) <= 0.1:
            # print('---------START TREE---------')
            v = self._tree_policy()
            # print('---------PASSOU DA TREE---------')
            # print('---------START ROLLOUT---------')
            reward = v.rollout()
            # print('---------PASSOU DO ROLLOUT---------')
            # print('---------START BACKPRP---------')
            v.backpropagate(reward)
            # print('---------PASSOU BACKPROP---------')
            # for i in self.state:
            #     # print(i)
        # print(self.children)
        # if len(self.children) == 0:
        #     self.passes += 1
        #     return 'pass'
        return self.best_child(c_param=0.)  

    
    def get_legal_actions(self,state,tile): 
        # # print('getting possible moves for ',tile)
        possibles = rev.getValidMoves(state,tile)
        # if possibles:
        #     self.passes = 0
        # else:
        #     self.passes +=1
        return possibles

    def is_game_over(self):
        # # print('PASSES:',self.passes)
        # # print('SHOULD BE PLAYER ',self.player)
        return True if self.passes >= 2 else False

    def game_result(self,state):
        temp = gb.get_points(state)
        pt = self.tile
        et = 'X' if pt == 'O' else 'O'
        if temp[pt] > temp[et]:
            return 1 #temp[pt] - temp[et]
        if temp[pt] == temp[et]:
            return 0
        if temp[pt] < temp[et]:
            return -1 #temp[et] - temp[pt]

    def move(self,state,tile,x,y):
        self.player = not self.player
        return gb.makeMove(state,tile,x,y)


def main():
    root = MonteCarloTreeSearchNode(state = initial_state)
    selected_node = root.best_action()
    return 