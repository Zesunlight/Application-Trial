# -*- coding: UTF-8 -*-
from collections import defaultdict
from bisect import bisect_left, bisect_right
from typing import Dict, List, Set
import numpy as np


class Resource:
    def __init__(self, core, memory):
        self.core_num = core
        self.memory_size = memory
        self.memory_core_rate = memory / core


class Server(Resource):
    def __init__(self, genre: str, core: int, memory: int, hardware: int, energy: int):
        super(Server, self).__init__(core, memory)
        self.genre = genre  # 长度不超过 20
        self.hardware_cost = hardware  # 不超过 5 × 10^5
        self.energy_cost = energy  # 不超过 5000
        self.a_core_num = self.b_core_num = core // 2
        self.a_memory_size = self.b_memory_size = memory // 2


class Virtual(Resource):
    # 对于每种类型的虚拟机，数据集保证至少存在一种服务器可以容纳
    def __init__(self, genre: str, core: int, memory: int, twin: bool):
        super(Virtual, self).__init__(core, memory)
        self.genre = genre  # 长度不超过 20
        self.is_twin = twin  # 不超过 5 × 10^5


class MyVirtual:
    def __init__(self, genre: str, request_id: str):
        self.genre = genre
        self.id = request_id  # 读出来的时候是字符串，就没做转换
        self.server_id = -1
        self.server_node = 'Z'


class MyServer(Resource):
    def __init__(self, genre: str, purchase_id: int):
        self.genre = genre
        self.id = purchase_id
        self.output_id = -1
        self.node = 'AB'

        s = genre_to_market_server[genre]
        super(MyServer, self).__init__(s.core_num, s.memory_size)
        self.a_core_num = s.a_core_num
        self.a_memory_size = s.a_memory_size
        self.b_core_num = s.b_core_num
        self.b_memory_size = s.b_memory_size

        self.update_cm_rate()
        self.add_to_distribute()

    def update_cm_rate(self):
        assert self.a_core_num >= 0
        assert self.a_memory_size >= 0
        if self.a_memory_size == 0:
            self.a_memory_core_rate = 0
            self.a_pos = 0
        elif self.a_core_num == 0:
            self.a_memory_core_rate = float('inf')
            self.a_pos = num_part - 1
        else:
            self.a_memory_core_rate = self.a_memory_size / self.a_core_num
            self.a_pos = bisect_right(slope, self.a_memory_core_rate) - 1

        assert self.b_core_num >= 0
        assert self.b_memory_size >= 0
        if self.b_memory_size == 0:
            self.b_memory_core_rate = 0
            self.b_pos = 0
        elif self.b_core_num == 0:
            self.b_memory_core_rate = float('inf')
            self.b_pos = num_part - 1
        else:
            self.b_memory_core_rate = self.b_memory_size / self.b_core_num
            self.b_pos = bisect_right(slope, self.b_memory_core_rate) - 1

        assert self.core_num >= 0
        assert self.memory_size >= 0
        if self.memory_size == 0:
            self.memory_core_rate = 0
            self.pos = 0
        elif self.core_num == 0:
            self.memory_core_rate = float('inf')
            self.pos = num_part - 1
        else:
            self.memory_core_rate = self.memory_size / self.core_num
            self.pos = bisect_right(slope, self.memory_core_rate) - 1

    def add_to_distribute(self):
        distribute_add(double_baby_breath[self.pos], self.core_num, self.memory_size, self.id)
        distribute_add(single_baby_breath[self.a_pos], self.a_core_num, self.a_memory_size, (self.id, 'A'))
        distribute_add(single_baby_breath[self.b_pos], self.b_core_num, self.b_memory_size, (self.id, 'B'))

    def remove_from_distribute(self):
        double_baby_breath[self.pos][self.core_num][self.memory_size].remove(self.id)
        single_baby_breath[self.a_pos][self.a_core_num][self.a_memory_size].remove((self.id, 'A'))
        single_baby_breath[self.b_pos][self.b_core_num][self.b_memory_size].remove((self.id, 'B'))

    def add_virtual(self, virtual_id: str):
        v = id_to_virtual[virtual_id]
        mv = genre_to_market_virtual[v.genre]
        self.remove_from_distribute()

        if v.server_node == 'AB':
            self.a_memory_size -= mv.memory_size // 2
            self.a_core_num -= mv.core_num // 2
            self.b_memory_size -= mv.memory_size // 2
            self.b_core_num -= mv.core_num // 2
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
        elif v.server_node == 'A':
            self.a_memory_size -= mv.memory_size
            self.a_core_num -= mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
        elif v.server_node == 'B':
            self.b_memory_size -= mv.memory_size
            self.b_core_num -= mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
        else:
            raise ValueError(f'add_virtual -> virtual id: {virtual_id}, server node error')

        self.update_cm_rate()
        self.add_to_distribute()

    def del_virtual(self, virtual_id):
        v = id_to_virtual[virtual_id]
        mv = genre_to_market_virtual[v.genre]
        self.remove_from_distribute()

        if v.server_node == 'AB':
            self.a_memory_size += mv.memory_size // 2
            self.a_core_num += mv.core_num // 2
            self.b_memory_size += mv.memory_size // 2
            self.b_core_num += mv.core_num // 2
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
        elif v.server_node == 'A':
            self.a_memory_size += mv.memory_size
            self.a_core_num += mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
        elif v.server_node == 'B':
            self.b_memory_size += mv.memory_size
            self.b_core_num += mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
        else:
            raise ValueError(f'del_virtual -> virtual id: {virtual_id}, server node error')

        self.update_cm_rate()
        self.add_to_distribute()


def distribute_add(distribute: Dict[int, Dict[int, Set]], core: int, memory: int, value):
    dc = distribute[core]
    if memory in dc:
        dc[memory].add(value)
    else:
        dc[memory] = {value}


def find_nearest_server(distribution: Dict, virtual: Virtual):
    distance = float('inf')
    server = None
    various_core = sorted(list(distribution.keys()))
    core_start = bisect_left(various_core, virtual.core_num)
    if core_start == len(various_core):
        return None

    for core in range(core_start, len(various_core)):
        vc = distribution[various_core[core]]
        various_memory = sorted(list(vc.keys()))
        memory_start = bisect_left(various_memory, virtual.memory_size)
        if (memory_start == len(various_memory)) or (len(vc[various_memory[memory_start]]) == 0):
            continue

        dis = (various_memory[memory_start] - virtual.memory_size) ** 2 + \
              (various_core[core] - virtual.core_num) ** 2
        if dis < distance:
            distance = dis
            server = list(vc[various_memory[memory_start]])[0]
    return server


# def retain_huge_amount(baby_breath: List[Dict[int, Dict[int, List[str]]]]):
#     candidates = []
#     for market_server in baby_breath:
#         product = 0
#         g = ''
#         for market_core in market_server.keys():
#             for market_memory in market_server[market_core].keys():
#                 for genre in market_server[market_core][market_memory]:
#                     s = genre_to_market_server[genre]
#                     if s.core_num * s.memory_size > product:
#                         g = genre
#                         product = s.core_num * s.memory_size
#         candidates.append(g)
#     return candidates
#
#
# def find_proper_server(baby_breath: List[Dict[int, Dict[int, List[str]]]], large_virtual: List):
#     candidates = []
#     for i in range(len(large_virtual)):
#         v = genre_to_market_virtual[large_virtual[i]]
#         market_server = baby_breath[i]
#         product = float('inf')
#         g = ''
#         for market_core in market_server.keys():
#             if market_core < v.core_num:
#                 continue
#             for market_memory in market_server[market_core].keys():
#                 if market_memory < v.memory_size:
#                     continue
#                 for genre in market_server[market_core][market_memory]:
#                     s = genre_to_market_server[genre]
#                     if s.core_num * s.memory_size < product:
#                         g = genre
#                         product = s.core_num * s.memory_size
#         candidates.append(g)
#     return candidates


def read_records():
    n = int(input())  # 可以采购的服务器类型数量, 1≤N≤100
    # market_server_core_memory_distribute: Dict[int, Dict[int, List[str]]]

    for i in range(n):
        # (型号, CPU 核数, 内存大小, 硬件成本, 每日能耗成本)
        genre, core, memory, hardware, energy = input()[1:-1].split(', ')
        market_server = Server(genre, int(core), int(memory), int(hardware), int(energy))
        genre_to_market_server[genre] = market_server
        pos = bisect_right(slope, market_server.memory_core_rate) - 1
        market_server_baby_breath[pos].append(genre)

    m = int(input())  # 售卖的虚拟机类型数量, 1≤M≤1000
    virtual_largest = [[0, 0] for _ in range(num_part)]
    for i in range(m):
        # (型号, CPU 核数, 内存大小, 是否双节点部署)
        genre, core, memory, twin = input()[1:-1].split(', ')
        market_virtual = Virtual(genre, int(core), int(memory), bool(int(twin)))
        genre_to_market_virtual[genre] = market_virtual
        pos = bisect_right(slope, market_virtual.memory_core_rate) - 1
        virtual_largest[pos][0] = max(virtual_largest[pos][0], int(core))
        virtual_largest[pos][1] = max(virtual_largest[pos][1], int(memory))

    candidates = ['' for _ in range(num_part)]
    for i in range(num_part):
        min_core, min_memory = virtual_largest[i][0] * 2, virtual_largest[i][1] * 2
        dis = float('inf')
        for genre in market_server_baby_breath[i]:
            s = genre_to_market_server[genre]
            if (s.core_num < min_core) or (s.memory_size < min_memory):
                continue
            temp_dis = (s.core_num - min_core)**2 + (s.memory_size - min_memory)**2
            if temp_dis < dis:
                candidates[i] = genre
                dis = temp_dis

    t = int(input())  # T 天的用户请求序列数据, 1≤T≤1000
    purchased_id, actual_id = 0, 0
    for i in range(t):
        r = int(input())  # 当天共有 R 条请求, 用户创建请求数量总数不超过 10^5
        today_purchase = defaultdict(list)
        for j in range(r):
            # (add, 虚拟机型号, 虚拟机 ID) 或 (del, 虚拟机 ID)
            request = input()[1:-1].split(', ')

            # if request[-1] == '939102148':
            #     print('here')

            if request[0] == 'add':
                _, genre, virtual_id = request
                id_to_virtual[virtual_id] = MyVirtual(genre, virtual_id)
                market_virtual = genre_to_market_virtual[genre]
                pos = bisect_right(slope, market_virtual.memory_core_rate) - 1
                if market_virtual.is_twin:
                    server_id = find_nearest_server(double_baby_breath[pos], market_virtual)
                    if server_id:
                        server = purchase_id_to_server[server_id]
                    else:
                        # 买新服务器
                        # new_server_genre = find_nearest_server(market_server_baby_breath[pos], market_virtual)
                        new_server_genre = candidates[pos]
                        server = MyServer(new_server_genre, purchased_id)
                        purchase_id_to_server[purchased_id] = server
                        today_purchase[new_server_genre].append(server)
                        purchased_id += 1

                    id_to_virtual[virtual_id].server_id = server.id
                    id_to_virtual[virtual_id].server_node = 'AB'
                    deploy_design.append([virtual_id, server.id])
                    server.add_virtual(virtual_id)
                else:
                    migrate_info = find_nearest_server(single_baby_breath[pos], market_virtual)
                    if migrate_info:
                        server = purchase_id_to_server[migrate_info[0]]
                        id_to_virtual[virtual_id].server_id = server.id
                        id_to_virtual[virtual_id].server_node = migrate_info[1]
                        deploy_design.append([virtual_id, server.id, migrate_info[1]])
                        server.add_virtual(virtual_id)
                    else:
                        # single_virtual = Virtual(genre + '*2', market_virtual.core_num * 2, market_virtual.memory_size * 2, False)
                        # new_server_genre = find_nearest_server(market_server_baby_breath[pos], single_virtual)
                        new_server_genre = candidates[pos]
                        server = MyServer(new_server_genre, purchased_id)

                        id_to_virtual[virtual_id].server_id = server.id
                        id_to_virtual[virtual_id].server_node = 'A'
                        deploy_design.append([virtual_id, server.id, 'A'])
                        server.add_virtual(virtual_id)

                        purchase_id_to_server[purchased_id] = server
                        today_purchase[new_server_genre].append(server)
                        purchased_id += 1
            else:
                _, virtual_id = request
                v = id_to_virtual[virtual_id]
                purchase_id_to_server[v.server_id].del_virtual(virtual_id)

        print(f'(purchase, {len(today_purchase.keys())})')
        for p, ss in today_purchase.items():
            print(f'({p}, {len(ss)})')
            for s in ss:
                s.output_id = actual_id
                actual_id += 1
        today_purchase.clear()
        print('(migration, 0)')
        for m in deploy_design:
            m[1] = purchase_id_to_server[m[1]].output_id
            if len(m) == 2:
                print(f'({m[1]})')
            elif len(m) == 3:
                print(f'({m[1]}, {m[2]})')
            else:
                raise ValueError(f'deploy_design error, {m}')
        deploy_design.clear()


if __name__ == '__main__':
    # 市场上的可选项
    genre_to_market_server: Dict[str, Server] = {}
    genre_to_market_virtual: Dict[str, Virtual] = {}
    # market_virtual_baby_breath: List[Dict[int, Dict[int, List[str]]]] = []

    # 实际的服务器和虚拟机
    purchase_id_to_server: Dict[int, MyServer] = {}
    id_to_virtual: Dict[str, MyVirtual] = {}  # 文件中的 id 到虚拟机实例

    double_baby_breath: List[Dict[int, Dict[int, Set[int]]]] = []  # 用于接收双节点虚拟机
    single_baby_breath: List[Dict[int, Dict[int, Set[tuple]]]] = []  # 用于接收单节点虚拟机

    slope = [0, 1/6, 1/5, 1/4, 1/3, 1/2, 1, 2, 3, 4, 5, 6]
    num_part = len(slope)  # 第一象限分成几部分
    # angle = np.linspace(0, np.pi/2, num_part + 1)[:-1]
    # slope = np.tan(angle)

    for _ in range(num_part):
        double_baby_breath.append(defaultdict(dict))
        single_baby_breath.append(defaultdict(dict))
        # market_server_baby_breath.append(defaultdict(dict))
        # market_virtual_baby_breath.append(defaultdict(dict))

    market_server_baby_breath: List[List] = [[] for _ in range(num_part)]
    deploy_design: List[List] = []
    read_records()
    # print('finish')
