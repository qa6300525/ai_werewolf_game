#!/usr/bin/env python
# coding: utf-8
import random
import utils
import aiagent


class Player:
    def __init__(self, player_id, player_name, role, ids, game_config_description=""):
        self.game = None
        self.player_id = player_id
        self.player_name = f"玩家{player_id}"
        self.role = role
        self.alive = True
        self.reason = ""
        self.vote_count = 0
        self.companion = []
        self.ai = aiagent.DialogueAgent(player_id, role, game_config_description)
        # 把所有玩家的角色都记录在一个字典里, 用于预言家查验身份
        self.player_roles_dict = {}
        if role == "预言家":
            for pid in ids:
                self.player_roles_dict[pid] = None
        self.analyze_dict = {}  # 存放分析结果

    def set_game(self, game):
        self.game = game

    def speak(self, strategies=None):
        """
        玩家发言
        :param strategies:
        :return:
        """
        if strategies is None:
            strategies = []
        strategies_str = "\n".join(strategies)

        action = f"""
rules:[禁止幻想没发生的事,禁止怀疑自己是狼人]
- Observation: 详细列出玩家「白天」交流的关键信息.
- Doubtful: Based on the observed information, raise doubts step-by-step ensuring logical clarity.
- Reasoning: Based on the observations and raised doubts, as well as the following strategies, infer the identities and possible scenarios of the players.
- Strategy: Choose one of the following as the best speaking strategy:
```
{strategies_str}.
```
- Said: Express your own views coherently based on the above steps(不要直接把Strategy说出来) in first person. Remember to use Chinese.
Format your response as a JSON object, with "Observation", "Doubtful", "Strategy", "Reasoning" and "Said" as the keys.
"""
        if self.role == "狼人":
            action = f"""
rules:[禁止关注夜晚信息，禁止怀疑同伴,查验同伴，禁止幻想没发生的事]
- Observation: 详细列出玩家白天交流的关键信息.
- Doubtful: Based on the observed information raise doubts step-by-step ensuring logical clarity.
- Strategy: Choose one of the following as the best speaking strategy:
```
{strategies_str}.
```
- Reasoning: 根据Observation、Doubtful和Strategy，推理其他玩家的身份，同时遵循游戏规则，确保自己和同伴的狼人身份不被暴露。
- Said: Express your own views coherently based on the above steps(不要直接把Strategy说出来) in first person. Remember to use Chinese.
Format your response as a JSON object, with "Observation", "Doubtful", "Strategy", "Reasoning" and "Said" as the keys.
"""
            if self.game.current_status.endswith("夜晚"):
                action = f"""
rules:[禁止怀疑同伴,查验同伴，禁止幻想没发生的事]
- Think: 同同伴沟通回答,作为狼人今夜我要杀谁？我认为哪位玩家可能是预言家？(禁止选择狼人同伴)
- Said: Express your own views coherently in first person. Remember to use Chinese.
Format your response as a JSON object, with "Think" and "Said" as the keys."""
        game_status_str, game_info_str = self.assembly_all(action)
        return self.ai.speak(game_status_str,
                             game_info_str)

    def assembly_all(self, action):
        private_log = []
        private_board = self.game.private_boards.get(self.role)
        if private_board:
            private_log = private_board.log
        companion_players = []
        if self.role == "狼人":
            companion_players = self.game.player_role_map_list.get(self.role)
        game_status_str = utils.assembly_status(self.game.current_status,
                                                self.game.get_active_player_ids(),
                                                companion_players,
                                                self.analyze_dict,
                                                action,
                                                player_role_dict=self.player_roles_dict)
        game_info_str = utils.assembly_information(self.game.game_log.log,
                                                   private_log)
        return game_status_str, game_info_str

    def analyze(self):
        """
        分析当前局势, 给AI思考用
        :return:
        """
        pass

    def vote(self, aim):
        example = """{"vote": -1}"""
        action = f"""Base on you and your companion communication, choose one players to vote.
        Format your response as a JSON object, e.g. {example}"""

        game_status_str, game_info_str = self.assembly_all(action)
        player_id = self.ai.common_vote(game_status_str, game_info_str)
        return player_id

    def vote_v1(self, aim) -> int:
        known = [f"玩家{self.player_id}是{self.role}"]
        if self.role == "狼人":
            known = []
            companion_players = self.game.player_role_map_list.get(self.role)
            for pid in companion_players:
                known.append(f"玩家{pid}是{self.role}")
            known.append("其余玩家不是狼人")
        if self.role == "预言家":
            known = [f"玩家{self.player_id}是{self.role}"]
            for pid, role in self.player_roles_dict.items():
                known.append(f"玩家{pid}是{role}")
            known.append("其余玩家不是预言家")
        action = f"""
        - Observation: 详细列出玩家「白天」交流的 key information.
        - Doubtful: Based on the observed information and game rules, raise doubts step-by-step ensuring logical clarity.
        - Reasoning: Based on the observations and raised doubts, as well as the following strategies, infer the identities and possible scenarios of the players.
        - Analyze:  Infer all players possible roles, based on the above steps, game rules and last analyze.
        Assign a score from 0 to 1 for each role (狼人, 平民, 预言家), with 0 meaning very unlikely and 1 meaning very likely. 
        Please also provide a brief explanation for your judgment.(Hint,你已知的身份信息:{known}""" + """
Use Chinese and Remember to follow the format as a JSON object: 
{"Observation":"","Doubtful":"","Reasoning":"","Analyze":[{"0":{"狼人":score,"预言家":score,"平民":score}},{"1":{"狼人":score,"预言家":score,"平民":score}},...,{"n":{"狼人":score,"预言家":score,"平民":score}}]}
"""
        game_status_str, game_info_str = self.assembly_all(action)

        analyze_dict = self.ai.common_vote_v1(game_status_str, game_info_str)
        while not utils.validate_data(analyze_dict):
            print("Your input format is wrong, please check and try again.")
            analyze_dict = self.ai.common_vote_v1(game_status_str, game_info_str)
        self.analyze_dict = analyze_dict

        # 获取分析结果中aim可能性最大的玩家
        max_p = -1
        player_id = -1
        role_infer_list = self.analyze_dict.get("Analyze")
        for role_dict in role_infer_list:
            for player, role_info in role_dict.items():
                temp_id = int(player)
                # 跳过已经死亡的玩家
                if temp_id not in self.game.get_active_player_ids():
                    continue
                # 预言家特殊逻辑，不投票给已经验过的玩家
                if self.player_roles_dict.get(temp_id) is not None:
                    continue
                # 狼人特殊逻辑，不投票给同伴
                if self.role == "狼人" and temp_id in self.game.player_role_map_list.get(self.role):
                    continue
                # 不能投票给自己
                if self.player_id == temp_id:
                    continue
                if role_info.get(aim) > max_p:
                    max_p = role_info.get(aim)
                    player_id = temp_id
        return player_id

    def use_potion(self, player_id, action):
        if self.role == "女巫":
            print(f"{self.player_name} used {action} on player {player_id}")

    def take_away(self, all_active_player_ids):
        if self.role == "猎人":
            if self.player_id in all_active_player_ids:
                all_active_player_ids.remove(self.player_id)
            player_id = random.choice(all_active_player_ids)
            return player_id

    def record_identity(self, player_id, role):
        if self.role == "预言家" and self.alive:
            self.player_roles_dict[player_id] = role
