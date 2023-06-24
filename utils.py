#!/usr/bin/env python
# coding: utf-8


def assembly_status(current_state, active_players,
                    companion_players, analyze_dict,
                    current_action, player_role_dict=None):
    assembly_str = f"Current time:{current_state}\n"
    assembly_str += f"Existing player:{active_players}\n"
    if len(companion_players) > 1:
        assembly_str += f"Companion player:{companion_players}\n"
    if len(analyze_dict) > 0:
        assembly_str += f"Last analyze:{analyze_dict}\n"
    if player_role_dict is not None:
        assembly_str += f"Player role:{player_role_dict}\n"
    assembly_str += f"\nDo actions with the following rules: {current_action}\n"
    # TODO 投票信息，玩家淘汰原因，

    return assembly_str


def assembly_information(cur_game_log: list, role_private_log: list) -> str:
    # 如果长度大于limit_length，就删除前面的
    limit_length = 20
    if len(cur_game_log) > limit_length:
        cur_game_log = cur_game_log[-limit_length:]
    if len(role_private_log) > limit_length:
        role_private_log = role_private_log[-limit_length:]
    temp_list = []
    temp_list.extend(cur_game_log)
    temp_list.extend(role_private_log)
    temp_list = sorted(temp_list, key=lambda x: x[0])
    msg = ""
    for i in temp_list:
        msg += f"{i[1]}\n"
    return msg


def check_list_format(data, expected_format):
    if not isinstance(data, list) or not isinstance(expected_format, list):
        return False

    a_keys = set(data[0].keys())
    b_keys = set(expected_format[0].keys())

    for dic in data:
        if set(dic.keys()) != a_keys:
            return False
    for dic in expected_format:
        if set(dic.keys()) != b_keys:
            return False

    return True


def validate_data(parsed_data):
    if not isinstance(parsed_data, dict):
        return False

    required_keys = ["Observation", "Doubtful", "Reasoning", "Analyze"]
    if not all(key in parsed_data for key in required_keys):
        return False

    if not isinstance(parsed_data["Analyze"], list):
        return False

    analyze_keys = {"狼人", "预言家", "平民"}
    for item in parsed_data["Analyze"]:
        if not isinstance(item, dict):
            return False
        for key, value in item.items():
            if not isinstance(value, dict):
                return False
            if not analyze_keys.issubset(value.keys()):
                return False
    return True


# if __name__ == '__main__':
#     a = {"Observation": [], "Doubtful": [], "Reasoning": [],
#          "Analyze": [{"0": {"狼人": -1, "预言家": -1, "平民": -1}}, {"1": {"狼人": -1, "预言家": -1, "平民": -1}}]}
#     print(validate_data(a))
#     max_p = -1
#     player_id = -1
#     aim = '狼人'
#     for role_dict in a["Analyze"]:
#         for player, role_info in role_dict.items():
#             print(player, role_info)
#             temp_id = int(player)
#             for role, score in role_info.items():
#                 print(role, score)
#                 if role_info.get(aim) > max_p:
#                     max_p = role_dict.get(aim)
#                     player_id = temp_id
#     print(max_p, player_id)


def text_to_json(text):
    lines = text.strip().split('\n')
    messages = []
    import json
    for line in lines:
        line = line.replace("：", ":")
        msg = line.split(':', 1)
        if ":" not in line or len(msg) != 2:
            continue
        sender, message = msg
        messages.append({'sender': sender.strip(), 'message': message.strip()})
    return json.dumps(messages, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    txt = """
    系统:游戏开始，第一天夜晚，
系统:预言家开始查验身份
玩家1:查验玩家 x 的身份， 玩家x 是 xx。
系统:狼人开始行动
玩家0:我认为今晚应该杀掉玩家3，他看起来比较可疑。至于预言家，我觉得可能是玩家1。
玩家5:我认为今晚我们应该杀掉玩家2，他看起来很有嫌疑。至于预言家，我还不确定是谁。
系统:狼人请投票：
玩家0：投票淘汰玩家x
玩家5：投票淘汰玩家y

系统:天亮了，第一天白天。
系统:今夜死的玩家是，淘汰玩家 3。
系统:首夜遗言:
玩家3: 虽然我在第一天的夜晚被淘汰了，但我会尽力协助真正的预言家，推理出谁是狼人。我观察到的交流信息不足以提出怀疑，但我会把我观察到的关键信息告诉真正的预言家。我相信我们可以一起找出狼人，保护平民。

系统:白天,玩家开始发言（注意：简版狼人杀，就从0号玩家开始发言）
玩家0: 我认为我们应该集中讨论玩家1的身份，他可能是狼人。另外，我觉得我们应该尽早找出真正的预言家，以便更好地推理出狼人的身份。我相信我们可以一起保护平民，找出狼人。
玩家1: 大家好，我是预言家玩家1。我在第一天的夜晚查验了玩家2的身份，他是平民。根据遗言，玩家3会协助真正的预言家推理出狼人的身份。我认为我们应该相信玩家3的话，找出真正的预言家来更好地推理。同时，我希望大家不要怀疑我是狼人，因为我已经给出了验人结果。我建议大家投票淘汰怀疑度比较高的玩家，保护平民。谢谢大家。
玩家2: 听到玩家1自称预言家，我感到有些怀疑。虽然他声称验人结果是我是平民，但我不能排除他是狼人伪装成预言家的可能性。我认为我们应该继续观察他的行动。此外，玩家0提出的怀疑也是有一定道理的，我们需要进一步观察。我打算继续观察玩家1和玩家0的行动，并在真正的预言家出现后配合他进行推理，找出狼人，保护平民。
玩家4: 我观察到玩家0怀疑玩家1是狼人，但我们需要进一步观察他的行动。玩家1自称是预言家，但我们需要找出真正的预言家，以便更好地推理出狼人的身份。同时，根据玩家3的首夜遗言，他会尽力协助真正的预言家推理出狼人的身份，我们应该尊重他的意见。我认为我们需要继续观察玩家1和玩家0的行动，并在真正的预言家出现后配合他进行推理，找出狼人，保护平民。
玩家5: 我认为我们需要继续观察玩家1的行动，确保他是真正的预言家。同时，我们也需要找出其他线索来证实或者否定玩家0的怀疑。玩家2的怀疑也需要进一步观察。最重要的是，我们需要找到真正的预言家，并在他的带领下，找出狼人，保护平民。
玩家6: 我认为我们需要尊重首夜遗言，尽快找到真正的预言家。虽然玩家1自称预言家，但他的验人结果并没有让其他玩家得到证实，我对他的身份产生了一些怀疑。同时，玩家0怀疑玩家1是狼人，玩家2对他的身份也表示怀疑。我需要继续观察他们的行动，寻找更多的线索。最重要的是，我们需要找到真正的预言家，并在他的带领下，推理出狼人的身份，保护平民。
白天:投票环节开始
系统:玩家 0 投票给玩家 4
系统:玩家 1 投票给玩家 0
系统:玩家 2 投票给玩家 0
系统:玩家 4 投票给玩家 0
系统:玩家 5 投票给玩家 1
系统:玩家 6 投票给玩家 1
系统:归票结果：玩家0，3票，玩家1,2票，玩家4,1票
系统:投票结果，放逐玩家 0，
系统:放逐遗言:
玩家0: 我认为我们应该尽快找到真正的预言家，并在他的带领下，推理出狼人的身份，保护平民。根据遗言，玩家3会尽力协助真正的预言家推理出狼人的身份，我们应该尊重他的意见。同时，玩家1自称预言家，但验人结果没有得到证实，也有可能是狼人伪装。我们需要进一步观察他的行动，寻找更多的证据和线索。此外，根据狼人的发言，玩家0和玩家5都是狼人，我们需要警惕他们的行动。最重要的是，我们需要团结起来，尽早找出狼人，保护平民。
系统:第二天，夜晚
系统:预言家开始查验身份：玩家1 查验玩家 x 的身份， 玩家x 是 xx。
系统:狼人开始行动
狼人开始投票淘汰人
第2天:白天，今夜死的是玩家1，没有遗言
玩家开始发言

玩家2: 我认为，我们需要尽快找到真正的预言家。同时，玩家1被淘汰，有可能是狼人。我们需要进一步观察其他玩家的行动，找到狼人的线索。我会配合真正的预言家，推理出狼人的身份，保护平民。
玩家4: 在昨天的投票中，玩家0被淘汰，但我们需要进一步观察其他玩家的行动，找到狼人的线索。根据预言家的验人结果，我们需要尊重他的结果，并在他的带领下，推理出狼人的身份，保护平民。我对玩家0和玩家5产生了怀疑，需要进一步观察他们的行动。玩家1被淘汰，有可能是狼人，其他玩家的身份也需要进一步观察。我会配合真正的预言家，推理出狼人的身份，保护平民。
玩家5: 我认为我们需要尽快找到真正的预言家，确定其他玩家的身份。根据玩家5的发言，我怀疑他是狼人，并试图引导其他玩家怀疑他。我们需要在不暴露自己和同伴的狼人身份的情况下，通过引导怀疑其他玩家来保护自己和同伴。
玩家6: 我观察到玩家1被淘汰，他有可能是预言家。我怀疑玩家0和玩家5是狼人，并会继续观察他们的行动。根据昨天的投票结果，玩家1很可能是狼人伪装成预言家。同时，我怀疑玩家5是狼人。我们需要尽快找到真正的预言家，并在他的带领下，推理出狼人的身份，保护平民。
系统:投票环节开始
系统:玩家 2 投票给玩家 5
系统:玩家 4 投票给玩家 5
系统:玩家 5 投票给玩家 2
系统:玩家 6 投票给玩家 5
系统:归票结果：玩家5，3票，玩家2,1票
系统:投票结果，放逐玩家 5
系统:游戏结束，平民阵营获胜！

系统:身份解密,狼人: 玩家0, 玩家5;预言家: 玩家1;平民: 玩家2, 玩家3, 玩家4, 玩家6
    """

    print(text_to_json(txt))
