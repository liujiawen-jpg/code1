import enum
from collections import namedtuple
# 枚举类型构造棋子


class Player(enum.Enum):
    black = 1
    white = 2

    @property #该装饰器创造只读属性方法不会被修改
    def other(self):
        if self == Player.white:
            return Player.black
        else:
            return Player.white
# 利用元祖来表示棋盘的十字交叉点
class Point(namedtuple('Point','row col')):
	def neighbors(self):
		return [
	Point(self.row-1,self.col),
	Point(self.row+1,self.col),
	Point(self.row,self.col-1),
	Point(self.row,self.col+1)
		]

