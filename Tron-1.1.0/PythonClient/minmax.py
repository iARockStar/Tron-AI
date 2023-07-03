import math
import copy
from ks.models import ECell, EDirection, Position, World
from ks.commands import ChangeDirection, ActivateWallBreaker


class Node:

    def __init__(self, parent, act, color, world, first_color):
        self.first_color = first_color
        self.act = act
        self.color = color
        if parent is None:
            self.world = copy.deepcopy(world)
        else:
            self.world = copy.deepcopy(parent.world)
        self.parent = parent

        self.score, self.world = self.evaluate_score(self.world)
        self.list_of_children = []
        self.isterminal = False

    def evaluate_score(self, world):
        empty_count = 0
        if self.color == "Blue":
            my_side = ECell.BlueWall
            other_side = ECell.YellowWall
            other_side_color = "Yellow"
            my_color = "Blue"

        else:
            my_side = ECell.YellowWall
            other_side = ECell.BlueWall
            other_side_color = "Blue"
            my_color = "Yellow"
        if self.act is None:
            is_full_count = self.calculate_empty_areas(empty_count, other_side_color, world)
            if self.first_color == "Yellow":
                return (world.agents[self.first_color].health * 200 + world.scores[self.first_color]) - \
                       (world.agents["Blue"].health * 200 +
                        world.scores["Blue"]) + (-3 if is_full_count else 0), world
            else:
                return (world.agents[self.first_color].health * 200 + world.scores[self.first_color]) - \
                       (world.agents["Yellow"].health * 200 +
                        world.scores["Yellow"]) + (-3 if is_full_count else 0), world

        world.board[world.agents[other_side_color].position.y][world.agents[other_side_color].position.x] = my_side
        world.scores[other_side_color] += world.constants.wall_score_coefficient

        if self.act == EDirection.Right:

            self.change(my_side, other_side, other_side_color, world, 1, 0, EDirection.Right)
        elif self.act == EDirection.Left:
            self.change(my_side, other_side, other_side_color, world, -1, 0, EDirection.Left)
        elif self.act == EDirection.Up:
            self.change(my_side, other_side, other_side_color, world, 0, -1, EDirection.Up)
        elif self.act == EDirection.Down:
            self.change(my_side, other_side, other_side_color, world, 0, 1, EDirection.Down)
        else:
            direction = world.agents[other_side_color].direction
            world.agents[other_side_color].wall_breaker_rem_time = world.constants.wall_breaker_duration + 1
            if direction == EDirection.Right:
                self.change(my_side, other_side, other_side_color, world, 1, 0, direction)
            elif direction == EDirection.Left:
                self.change(my_side, other_side, other_side_color, world, -1, 0, direction)
            elif direction == EDirection.Up:
                self.change(my_side, other_side, other_side_color, world, 0, -1, direction)
            else:
                self.change(my_side, other_side, other_side_color, world, 0, 1, direction)

        if world.agents[other_side_color].health == 0:
            self.isterminal = True

        is_full_count = self.calculate_empty_areas(empty_count, other_side_color, world)

        if self.first_color == "Yellow":
            return (world.agents[self.first_color].health * 200 + world.scores[self.first_color]) - \
                   (world.agents["Blue"].health * 200 +
                    world.scores["Blue"]) + (-3 if is_full_count else 0), world
        else:
            return (world.agents[self.first_color].health * 200 + world.scores[self.first_color]) - \
                   (world.agents["Yellow"].health * 200 + world.scores["Yellow"]) + \
                   (-3 if is_full_count else 0), world

    def calculate_empty_areas(self, empty_count, other_side_color, world):
        my_pos_x = world.agents[self.first_color].position.x
        my_pos_y = world.agents[self.first_color].position.y
        if my_pos_x - 1 >= 0:
            if my_pos_y - 1 >= 0 and world.board[my_pos_y - 1][my_pos_x - 1] != ECell.Empty:
                empty_count -= 1
            if world.board[my_pos_y][my_pos_x - 1] != ECell.Empty:
                empty_count -= 1
            if my_pos_y + 1 < len(world.board) and world.board[my_pos_y + 1][my_pos_x - 1] != ECell.Empty:
                empty_count -= 1
        if my_pos_x + 1 < len(world.board[0]):
            if my_pos_y - 1 >= 0 and world.board[my_pos_y - 1][my_pos_x + 1] != ECell.Empty:
                empty_count -= 1
            if world.board[my_pos_y][my_pos_x + 1] != ECell.Empty:
                empty_count -= 1
            if my_pos_y + 1 < len(world.board) and world.board[my_pos_y + 1][my_pos_x + 1] != ECell.Empty:
                empty_count -= 1
        if my_pos_y - 1 >= 0 and world.board[my_pos_y - 1][my_pos_x] != ECell.Empty:
            empty_count -= 1
        if my_pos_y + 1 < len(world.board) and world.board[my_pos_y + 1][my_pos_x] != ECell.Empty:
            empty_count -= 1
        return empty_count == -8

    def change(self, my_side, other_side, other_side_color, world, x_val, y_val, direction):
        self.world.agents[other_side_color].direction = direction
        if world.agents[other_side_color].wall_breaker_cooldown > 0:
            world.agents[other_side_color].wall_breaker_cooldown -= 1

        if world.board[world.agents[other_side_color].position.y + y_val][
            world.agents[other_side_color].position.x + x_val] == ECell.AreaWall:
            world.agents[other_side_color].health = 0
            world.scores[other_side_color] -= world.constants.area_wall_crash_score

        elif world.board[world.agents[other_side_color].position.y + y_val][
            world.agents[other_side_color].position.x + x_val] == other_side or \
                world.board[world.agents[other_side_color].position.y + y_val][
                    world.agents[other_side_color].position.x + x_val] == my_side:
            if world.board[world.agents[other_side_color].position.y + y_val][
                world.agents[other_side_color].position.x + x_val] == other_side:
                world.scores[other_side_color] -= world.constants.wall_score_coefficient
            else:
                world.scores[self.color] -= world.constants.wall_score_coefficient
            if world.agents[other_side_color].wall_breaker_rem_time > 0 or world.agents[other_side_color].health > 1:
                if world.agents[other_side_color].wall_breaker_rem_time > 0:
                    world.agents[other_side_color].wall_breaker_rem_time -= 1

                    if world.agents[other_side_color].wall_breaker_rem_time == 0:
                        world.agents[other_side_color].health -= 1
                        if world.agents[other_side_color].health == 0:
                            if world.board[world.agents[other_side_color].position.y + y_val][
                                world.agents[other_side_color].position.x + x_val] == other_side:
                                world.scores[other_side_color] -= world.constants.my_wall_crash_score
                            else:
                                world.scores[other_side_color] -= world.constants.enemy_wall_crash_score
                        world.agents[other_side_color].wall_breaker_cooldown = world.constants.wall_breaker_cooldown
                else:
                    world.agents[other_side_color].health -= 1
                    if world.agents[other_side_color].health == 0:
                        if world.board[world.agents[other_side_color].position.y + y_val][
                            world.agents[other_side_color].position.x + x_val] == other_side:
                            world.scores[other_side_color] -= world.constants.my_wall_crash_score
                        else:
                            world.scores[other_side_color] -= world.constants.enemy_wall_crash_score


            elif world.agents[other_side_color].wall_breaker_rem_time == 0 and world.agents[
                other_side_color].health == 1:
                world.agents[other_side_color].health = 0
                if world.board[world.agents[other_side_color].position.y + y_val][
                    world.agents[other_side_color].position.x + x_val] == other_side:
                    world.scores[other_side_color] -= world.constants.my_wall_crash_score
                else:
                    world.scores[other_side_color] -= world.constants.enemy_wall_crash_score

        elif world.agents[other_side_color].position == world.agents[self.color].position:
            world.agents[other_side_color].health = 0
            world.scores[other_side_color] -= 2 * world.constants.area_wall_crash_score

        if world.agents[other_side_color].health != 0:
            world.agents[other_side_color].position.x += x_val
            world.agents[other_side_color].position.y += y_val
            world.board[world.agents[other_side_color].position.y][
                world.agents[other_side_color].position.x] = ECell.Empty

    def add_child(self, child_node):
        self.list_of_children.append(child_node)


class Tree:

    def __init__(self, node):
        self.node = node


class MiniMax:

    def __init__(self, tree):
        self.tree = tree
        self.root = tree.node

    def initial_make_tree(self):
        self.make_tree(self.root, 7)

    def make_tree(self, node, depth):
        if depth == 0 or node.isterminal:
            return
        moves = [EDirection.Right, EDirection.Left, EDirection.Up, EDirection.Down, "WallBreaker"]
        if node.world.agents[node.color].position.x + 1 == len(node.world.board[0]):
            moves.remove(EDirection.Right)
        if node.world.agents[node.color].position.x - 1 == -1:
            moves.remove(EDirection.Left)
        if node.world.agents[node.color].position.y + 1 == len(node.world.board):
            moves.remove(EDirection.Down)
        if node.world.agents[node.color].position.y - 1 == -1:
            moves.remove(EDirection.Up)
        if node.world.agents[node.color].direction == EDirection.Right:
            if EDirection.Left in moves:
                moves.remove(EDirection.Left)

        elif node.world.agents[node.color].direction == EDirection.Left:
            if EDirection.Right in moves:
                moves.remove(EDirection.Right)
        elif node.world.agents[node.color].direction == EDirection.Up:
            if EDirection.Down in moves:
                moves.remove(EDirection.Down)
        elif node.world.agents[node.color].direction == EDirection.Down:
            if EDirection.Up in moves:
                moves.remove(EDirection.Up)

        right_f = False
        up_f = False
        down_f = False
        left_f = False
        if node.world.agents[node.color].position.x - 1 >= 0:
            left_f = True
            left_pos = node.world.agents[node.color].position.x - 1
        if node.world.agents[node.color].position.x + 1 < len(node.world.board[0]):
            right_f = True
            right_pos = node.world.agents[node.color].position.x + 1
        if node.world.agents[node.color].position.y - 1 >= 0:
            up_f = True
            up_pos = node.world.agents[node.color].position.y - 1
        if node.world.agents[node.color].position.y + 1 < len(node.world.board):
            down_f = True
            down_pos = node.world.agents[node.color].position.y + 1

        direction = node.world.agents[node.color].direction
        flag = False
        if right_f:
            if direction == EDirection.Right:
                if node.world.board[node.world.agents[node.color].position.y][right_pos] == ECell.Empty or \
                        node.world.board[node.world.agents[node.color].position.y][right_pos] == ECell.AreaWall:
                    flag = True
        if left_f:
            if direction == EDirection.Left:
                if node.world.board[node.world.agents[node.color].position.y][left_pos] == ECell.Empty or \
                        node.world.board[node.world.agents[node.color].position.y][left_pos] == ECell.AreaWall:
                    flag = True

        if down_f:
            if direction == EDirection.Down:
                if node.world.board[down_pos][node.world.agents[node.color].position.x] == ECell.Empty or \
                        node.world.board[down_pos][node.world.agents[node.color].position.x] == ECell.AreaWall:
                    flag = True

        if up_f:
            if direction == EDirection.Up:
                if node.world.board[up_pos][node.world.agents[node.color].position.x] == ECell.Empty or \
                        node.world.board[up_pos][node.world.agents[node.color].position.x] == ECell.AreaWall:
                    flag = True

        if node.world.agents[node.color].wall_breaker_cooldown > 0 or node.world.agents[
            node.color].wall_breaker_rem_time > 0:
            moves.remove("WallBreaker")

        if flag:
            if "WallBreaker" in moves:
                moves.remove("WallBreaker")

        for move in moves:

            if node.color == "Blue":
                child_node = Node(node, move, "Yellow", None, node.first_color)

            elif node.color == "Yellow":
                child_node = Node(node, move, "Blue", None, node.first_color)

            node.add_child(child_node)
            self.make_tree(child_node, depth - 1)

    def initial_minimax(self):
        return self.minimax_alpha_beta(self.root, 7, -math.inf, math.inf, True)

    def minimax_alpha_beta(self, node, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return node.act, node.score

        if maximizing_player:
            value = -math.inf
            best_move = None
            for move in node.list_of_children:
                new_move = move.act
                child_node = move
                child_act, child_value = self.minimax_alpha_beta(child_node, depth - 1, alpha, beta, False)
                if child_value > value:
                    value = child_value
                    best_move = new_move
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return best_move, value
        else:
            value = math.inf
            best_move = None
            for move in node.list_of_children:
                child_node = move
                new_move = move.act
                child_act, child_value = self.minimax_alpha_beta(child_node, depth - 1, alpha, beta, True)
                if child_value < value:
                    value = child_value
                    best_move = new_move
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return best_move, value
