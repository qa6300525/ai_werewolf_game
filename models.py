#!/usr/bin/env python
# coding: utf-8
import random
import time
from model_player import Player
import aiagent
import utils
import const


class GameLog:
    static_variable = 0

    def __init__(self, log_type="公共"):
        self.log_type = log_type
        self.log = []

    def add_log(self, log):
        GameLog.static_variable += 1
        log = f"{self.log_type}-{log}"
        self.log.append((GameLog.static_variable, log))
        print(log)


class Game:
    def __init__(self, players):
        # self.day_count = 0
        self.players = players
        self.current_player = None
        self.game_state = "进行中"
        self.game_winner = None
        self.day_count = 0  # 游戏天数
        self.game_log = GameLog()  # 记录游戏过程
        self.player_role_map_list = {}  # 记录每个角色的玩家
        self.private_boards = {}  # 记录特殊角色夜晚沟通信息
        self.last_voted_person = None  # 记录上一次被投票放逐
        for player in players:
            player.set_game(self)
            if player.role in self.player_role_map_list:
                self.player_role_map_list[player.role].append(player.player_id)
            else:
                self.player_role_map_list[player.role] = [player.player_id]
            if player.role in ["预言家", "狼人", "女巫"]:
                self.private_boards[player.role] = GameLog(player.role)
        print(self.player_role_map_list)
        self.current_status = ""

    def game_loop(self):
        while self.game_state == "进行中":
            self.day_count += 1
            self.current_status = f"第{self.day_count}天:夜晚"
            self.night_phase()
            self.check_game_over()
            if self.game_state != "进行中":
                break
            if self.day_count == 1:
                # 首夜有遗言
                self.current_status = f"第{self.day_count}天:首夜遗言"
                self.last_words_phase()
            time.sleep(2)
            self.current_status = f"第{self.day_count}天:白天"
            self.day_phase()
            self.check_game_over()
            self.current_status = f"第{self.day_count}天:遗言"
            self.last_words_phase()
            time.sleep(2)

    def save_game(self):
        # 玩家信息
        all_log = ""
        player_info = ""
        for player in self.players:
            player_info += f"{player.player_name}-{player.role}-{player.alive}\n"
        # 玩家角色信息
        player_info += "\n"
        for role, player_list in self.player_role_map_list.items():
            player_info += f"{role}: {player_list}\n"
        all_log += player_info
        # 游戏信息
        temp_list = []
        temp_list.extend(self.game_log.log)
        # 特殊角色信息
        for role, game_log in self.private_boards.items():
            temp_list.extend(game_log.log)
        temp_list = sorted(temp_list, key=lambda x: x[0])
        all_log += "\n"
        for log in temp_list:
            all_log += f"{log[0]},{log[1]}\n"

        all_log += "\n"
        # 游戏结果
        all_log += self.game_winner
        cur_time_str = time.strftime("%m-%d-%H-%M-%S", time.localtime())
        with open(f"./log/game_log_{cur_time_str}.txt", "w") as f:
            f.write(all_log)

    def night_phase(self):
        self.game_log.add_log(self.current_status)

        # 预言家查验身份
        self.game_log.add_log(f"{self.current_status}: 预言家开始查验身份")
        for player in self.players:
            if player.role == "预言家" and player.alive:
                if self.day_count == 1:
                    aim = const.const_dict.get("查验")
                    check_player_id = player.vote(aim)
                else:
                    check_player_id = player.vote_v1("狼人")
                role = self.players[check_player_id].role
                self.private_boards["预言家"].add_log(f"{self.current_status}: "
                                                   f"玩家{player.player_id} 查验玩家 {check_player_id} 的身份是 {role}")
                player.player_roles_dict[check_player_id] = role
        # 狼人行动
        self.game_log.add_log(f"{self.current_status}: 狼人开始行动")
        for player in self.players:
            if player.role == "狼人" and player.alive:
                action_log = player.speak(["与同伴确定今晚从其他人中淘汰最大威胁的玩家"])  # 狼人夜晚沟通
                action_log = f"{self.current_status}:玩家{player.player_id}:{action_log}"
                self.private_boards["狼人"].add_log(action_log)

        # 狼人投票决定淘汰人角色编号
        self.game_log.add_log(f"{self.current_status}: 狼人开始投票淘汰人")
        victim_dict = {}
        for player in self.players:
            if player.role == "狼人" and player.alive:
                if self.day_count == 1:
                    victim_id = player.vote("预言家")
                else:
                    victim_id = player.vote_v1("预言家")
                if victim_id == -1:
                    continue
                victim_dict[victim_id] = victim_dict.get(victim_id, 0) + 1
                action_log = f"{self.current_status}:玩家{player.player_id}投票淘汰玩家{victim_id}"
                self.private_boards["狼人"].add_log(action_log)
        # 统计狼人投票结果
        victim_id = max(victim_dict, key=victim_dict.get)
        self.game_log.add_log(f"{self.current_status}: 狼人投票结果，淘汰玩家 {victim_id}")
        self.update_player_status(victim_id, False, "淘汰")

        # 女巫行动
        # self.game_log.add_log(f"{self.current_status}:女巫开始行动")
        for player in self.players:
            if player.role == "女巫" and player.alive:
                # 女巫救人
                saved_player_id = 0  # 假设救的玩家ID是0
                action_log = player.use_potion(saved_player_id, "救人")
                if action_log:
                    self.game_log.add_log(action_log)
                # 女巫毒人
                poisoned_player_id = 1  # 假设毒的玩家ID是1
                action_log = player.use_potion(poisoned_player_id, "毒人")
                if action_log:
                    self.game_log.add_log(action_log)
        # 猎人行动
        # self.game_log.add_log(f"{self.current_status}: 猎人开始行动")
        for player in self.players:
            if player.role == "猎人" and not player.alive:
                action_log = player.take_away(2)  # 假设带走的玩家ID是2
                if action_log:
                    self.game_log.add_log(action_log)

    def day_phase(self):
        self.game_log.add_log(self.current_status)
        self.game_log.add_log(f"{self.current_status}:玩家开始发言")
        for player in self.players:
            if player.alive:
                speech = player.speak(const.speech_strategy.get(player.role))
                action_log = f"{self.current_status}:玩家{player.player_id}: {speech}"
                self.game_log.add_log(action_log)

        self.game_log.add_log(f"{self.current_status}:投票环节开始")
        vote_dict = {}
        for player in self.players:
            if player.alive:
                aim = "狼人"
                if player.role == "狼人":
                    aim = "预言家"
                player_id = player.vote_v1(aim)
                # 计票, 如果player_id == -1, 则表示弃票
                if player_id != -1:
                    vote_dict[player_id] = vote_dict.get(player_id, 0) + 1
                self.game_log.add_log(f"{self.current_status}:玩家 {player.player_id} 投票给玩家 {player_id}")
        # 统计投票结果
        victim_id = max(vote_dict, key=vote_dict.get)
        # 放逐玩家
        self.update_player_status(victim_id, False, "放逐")
        self.game_log.add_log(f"{self.current_status}:投票结果，放逐玩家 {victim_id}")

    def update_player_status(self, player_id, status, reason=None):
        for player in self.players:
            if player.player_id == player_id:
                player.alive = status
                player.reason = reason
                self.last_voted_person = player_id
                break

    # 遗言环节
    def last_words_phase(self):
        # self.game_log.add_log(self.current_status)
        for player in self.players:
            if player.player_id == self.last_voted_person:
                speech = player.speak(const.last_words_strategy.get(player.role))
                action_log = f"{self.current_status}:玩家{player.player_id}: {speech}"
                self.game_log.add_log(action_log)
                break

    def display_private_board(self, role):
        if role in self.private_boards:
            return "\n".join(self.private_boards[role].log)
        return "No private board for this role"

    def assign_roles(self, num_players):
        pass

    def display_role(self, player_id):
        print(self.players[player_id].role)

    def get_active_player_ids(self):
        return [player.player_id for player in self.players if player.alive]

    def get_role_count(self):
        role_count = {}
        for player in self.players:
            if player.alive:
                role_count[player.role] = role_count.get(player.role, 0) + 1
        return role_count

    def check_game_over(self):
        werewolves_count = 0
        villagers_count = 0
        for player in self.players:
            if player.alive:
                if player.role == "狼人":
                    werewolves_count += 1
                elif player.role != "狼人":
                    villagers_count += 1

        if werewolves_count == 0 or villagers_count <= werewolves_count or (
                werewolves_count == 1 and villagers_count == 1):
            self.game_state = "已结束"
            if werewolves_count == 0:
                self.game_winner = f"游戏结束，平民阵营获胜！{self.get_role_count()}"
                self.game_log.add_log(self.game_winner)
            else:
                self.game_winner = f"游戏结束，狼人阵营获胜！{self.get_role_count()}"
                self.game_log.add_log(self.game_winner)
            self.save_game()
            return True
        return False


def init_players(player_size):
    player_names = []
    ids = [i for i in range(player_size)]
    roles = ["狼人", "狼人", "预言家", "平民", "平民", "平民", "平民", "平民"]

    roles = roles[:player_size]
    for i in range(player_size):
        player_names.append("玩家" + str(i))

    game_config_description = f"游戏配置：{player_size}人局，"
    game_config_description += "，".join([f"{role}:{roles.count(role)}人" for role in set(roles)])
    print(game_config_description)
    # 打散角色顺序
    random.shuffle(roles)
    players = []
    for idx, name in enumerate(player_names):
        player = Player(idx, name, roles[idx], ids, game_config_description)
        players.append(player)
    return players


if __name__ == '__main__':
    # 初始化玩家
    g_players = init_players(5)
    for p in g_players:
        print(f"{p.player_id} {p.player_name} {p.role}")
    # 初始化游戏
    game = Game(g_players)
    # 开始游戏
    game.game_loop()
