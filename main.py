#!/usr/bin/env python
# coding: utf-8

import models

if __name__ == '__main__':
    # 初始化玩家
    g_players = models.init_players(7)
    # 初始化游戏
    game = models.Game(g_players)
    # 开始游戏
    game.game_loop()
