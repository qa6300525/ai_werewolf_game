#!/usr/bin/env python
# coding: utf-8


const_dict = {
    "查验": "checked",
    "毒药": "poisoned",
    "救人": "saved",
    "投票": "voted",
    "淘汰": "elimination",
    "放逐": "exiled",
}

speech_strategy = {
    "狼人": ["模仿预言家的发言，给出引导性信息",
           "模仿平民的发言，给出引导性信息",
           "如果有人声称自己是预言家，试图引导其他玩家对预言家的身份产生怀疑",
           "我认为哪位玩家可能是最大威胁？我如何判断的？避免暴露的情况下，我打算如何采取行动？",
           "通过引导怀疑其他玩家，避免透露自己和同伴的狼人身份"],
    "预言家": ["阐明自己的身份，给出验人结果，引导平民投票"],
    "女巫": ["我是女巫", "我是好人"],
    "猎人": ["我是猎人", "我是好人"],
    "白痴": ["我是白痴", "我是好人"],
    "守卫": ["我是守卫", "我是好人"],
    "平民": ["根据观察和推理，作为平民认可首夜遗言，白天我应该怎么发言？应该采取什么行动？"
           ],
}

last_words_strategy = {
    "狼人": ["你被淘汰了，现在是遗言阶段，从预言家的视角，给出引导性的发言",
           "你被淘汰了，现在是遗言阶段，从平民视角，给出引导性的发言",
           ],
    "预言家": ["你被淘汰了，现在是遗言阶段, 阐明自己的身份，给出验人结果，引导平民投票"],
    "女巫": ["我是女巫", "我是好人"],
    "猎人": ["我是猎人", "我是好人"],
    "白痴": ["我是白痴", "我是好人"],
    "守卫": ["我是守卫", "我是好人"],
    "平民": ["被淘汰了，作为平民应该怎么发表设么遗言？应该采取什么行动？",
           ]

}
