import copy
from .gotypes import Player


class Move():
    def __init__(self, point=None, is_pass=False, is_regin=False):
        assert (point is not None) ^ is_pass ^ is_regin
        self.point = point
        self.is_play = (point is not None)  # 落子
        self.is_pass = is_pass  # 跳过
        self.is_regin = is_regin  # 认输

    @classmethod  # classmethod 修饰符对应的函数不需要实例化
    def play(cls, point):
        return Move(point=point)  # 在棋盘上落下一颗棋子

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def regin(cls):
        return Move(is_regin=True)


class GoString():
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def remove_liberty(self, point):
        self.liberties.remove(point)
    # def remove_liberty(self, point):
    #   self.liberties.remove(point)

    def add_liberty(self, point):
        self.liberties.add(point)

    def merged_with(self, go_string):  # 合并棋链的函数
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones)  # 气指的是棋链还剩的气眼

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties
    # 比较两个值是否相等


class Board():  # 定义棋盘类
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):  # 返回棋盘交叉点的颜色
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point):  # 返回一个交叉点上的整条棋链
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    # def place_stone(self, player, point):
    #     assert self.is_on_grid(point)
    #     assert self._grid.get(point) is None
    #     adjacent_same_color = []
    #     adjacent_opposiet_color = []
    #     liberties = []
    #     for neighbor in point.neighbors():
    #         if not self.is_on_grid(neighbor):
    #             continue
    #         # pdb.set_trace()
    #         neighbor_string = self._grid.get(neighbor)

    #         if neighbor_string is None:
    #             liberties.append(neighbor)  # 如果没被占据说明还有气那么我们增加
    #         elif neighbor_string.color == player:
    #             if neighbor_string not in adjacent_same_color:

    #                 adjacent_same_color.append(neighbor_string)
    #         else:
    #             if neighbor_string not in adjacent_opposiet_color:
    #                 adjacent_opposiet_color.append(neighbor_string)
    #         new_string = GoString(player, [point], liberties)
    #         for same_color_string in adjacent_same_color:
    #             new_string = new_string.merged_with(same_color_string)
    #         for new_string_point in new_string.stones:
    #             self._grid[new_string_point] = new_string
    #         for other_color_string in adjacent_opposiet_color:
    #             other_color_string.remove_liberty(point)  # 减少对面棋子的气
    #         for other_color_string in adjacent_opposiet_color:
    #             if other_color_string.num_liberties == 0:
    #                 self._remove_string(other_color_string)
    #                 # 如果气全部提走，那么我们将该链全部取消
    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbor in point.neighbors():  # <1>
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)
# <1> First, we examine direct neighbors of this point.
# end::board_place_0[]
# tag::board_place_1[]
        for same_color_string in adjacent_same_color:  # <1>
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        for other_color_string in adjacent_opposite_color:  # <2>
            other_color_string.remove_liberty(point)
        for other_color_string in adjacent_opposite_color:  # <3>
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)
    def _remove_string(self, string):
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)  # 如果一个棋链被提走则气会增加
            self._grid[point] = None
# 游戏状态类包括棋子中的下一回合执子方，上一回合的游戏状态以及上一步动作


class GameState():
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        self.last_move = move

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)  # 深度拷贝，被复制的对象作为一个新的对象存在
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_regin:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass  # 如果两方都选择不下那么本局结束

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0  # 判断是否到自吃的地步

    @property
    def situation(self):
        return (self.next_player, self.board)

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board)  # 这个状态代表即将下子的人和当前棋局的样子
        past_state = self.previous_state
        while past_state is not None:
            if past_state.situation == next_situation:
                return True
            past_state = past_state.previous_state  # 个人感觉这个速度挺慢的
        return False

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_regin:
            return True
        return (
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.next_player, move) and
            not self.does_move_violate_ko(self.next_player, move)

        )
