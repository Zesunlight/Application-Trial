# -*- coding: UTF-8 -*-
from collections import defaultdict
from bisect import bisect_left
from typing import Dict, List


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
        self.a_memory_core_rate = self.a_memory_size / self.a_core_num
        self.b_core_num = s.b_core_num
        self.b_memory_size = s.b_memory_size
        self.b_memory_core_rate = self.b_memory_size / self.b_core_num
        self.memory_core_rate = self.memory_size / self.core_num
        # self.update_cm_rate()

        # dsc = double_server_distribute[self.core_num]
        # if self.memory_size in dsc:
        #     dsc[self.memory_size].add(self.id)
        # else:
        #     dsc[self.memory_size] = {self.id}
        # ssc = single_server_distribute[self.a_core_num]
        # if self.a_memory_size in ssc:
        #     ssc[self.a_memory_size].add((self.id, 'A'))
        #     ssc[self.a_memory_size].add((self.id, 'B'))
        # else:
        #     ssc[self.a_memory_size] = {(self.id, 'A'), (self.id, 'B')}
        self.update_distribute()

    def update_cm_rate(self):
        if self.a_core_num > 0:
            self.a_memory_core_rate = self.a_memory_size / self.a_core_num
        if self.b_core_num > 0:
            self.b_memory_core_rate = self.b_memory_size / self.b_core_num
        if self.core_num > 0:
            self.memory_core_rate = self.memory_size / self.core_num

    def update_distribute(self):
        distribute_add(double_server_distribute, self.core_num, self.memory_size, self.id)
        distribute_add(single_server_distribute, self.a_core_num, self.a_memory_size, (self.id, 'A'))
        distribute_add(single_server_distribute, self.b_core_num, self.b_memory_size, (self.id, 'B'))

    def add_virtual(self, virtual_id: str):
        v = id_to_virtual[virtual_id]
        mv = genre_to_market_virtual[v.genre]
        if v.server_node == 'AB':
            double_server_distribute[self.core_num][self.memory_size].remove(self.id)
            single_server_distribute[self.a_core_num][self.a_memory_size].remove((self.id, 'A'))
            single_server_distribute[self.b_core_num][self.b_memory_size].remove((self.id, 'B'))
            self.a_memory_size -= mv.memory_size // 2
            self.a_core_num -= mv.core_num // 2
            self.b_memory_size -= mv.memory_size // 2
            self.b_core_num -= mv.core_num // 2
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
            self.update_distribute()
        elif v.server_node == 'A':
            double_server_distribute[self.core_num][self.memory_size].remove(self.id)
            single_server_distribute[self.a_core_num][self.a_memory_size].remove((self.id, 'A'))
            self.a_memory_size -= mv.memory_size
            self.a_core_num -= mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
            distribute_add(double_server_distribute, self.core_num, self.memory_size, self.id)
            distribute_add(single_server_distribute, self.a_core_num, self.a_memory_size, (self.id, 'A'))
        elif v.server_node == 'B':
            double_server_distribute[self.core_num][self.memory_size].remove(self.id)
            single_server_distribute[self.b_core_num][self.b_memory_size].remove((self.id, 'B'))
            self.b_memory_size -= mv.memory_size
            self.b_core_num -= mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
            distribute_add(double_server_distribute, self.core_num, self.memory_size, self.id)
            distribute_add(single_server_distribute, self.b_core_num, self.b_memory_size, (self.id, 'B'))
        else:
            raise ValueError(f'add_virtual -> virtual id: {virtual_id}, server node error')

        if (self.a_core_num < 0) or (self.a_memory_size < 0) or (self.b_core_num < 0) or (self.b_memory_size < 0):
            raise ValueError(f"virtual_id: {virtual_id}, server_id: {self.id}, server_genre: {self.genre}")

    def del_virtual(self, virtual_id):
        v = id_to_virtual[virtual_id]
        mv = genre_to_market_virtual[v.genre]
        if v.server_node == 'AB':
            double_server_distribute[self.core_num][self.memory_size].remove(self.id)
            single_server_distribute[self.a_core_num][self.a_memory_size].remove((self.id, 'A'))
            single_server_distribute[self.b_core_num][self.b_memory_size].remove((self.id, 'B'))
            self.a_memory_size += mv.memory_size // 2
            self.a_core_num += mv.core_num // 2
            self.b_memory_size += mv.memory_size // 2
            self.b_core_num += mv.core_num // 2
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
            self.update_distribute()
        elif v.server_node == 'A':
            double_server_distribute[self.core_num][self.memory_size].remove(self.id)
            single_server_distribute[self.a_core_num][self.a_memory_size].remove((self.id, 'A'))
            self.a_memory_size += mv.memory_size
            self.a_core_num += mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
            distribute_add(double_server_distribute, self.core_num, self.memory_size, self.id)
            distribute_add(single_server_distribute, self.a_core_num, self.a_memory_size, (self.id, 'A'))
        elif v.server_node == 'B':
            double_server_distribute[self.core_num][self.memory_size].remove(self.id)
            single_server_distribute[self.b_core_num][self.b_memory_size].remove((self.id, 'B'))
            self.b_memory_size += mv.memory_size
            self.b_core_num += mv.core_num
            self.memory_size = min(self.a_memory_size, self.b_memory_size) * 2
            self.core_num = min(self.a_core_num, self.b_core_num) * 2
            distribute_add(double_server_distribute, self.core_num, self.memory_size, self.id)
            distribute_add(single_server_distribute, self.b_core_num, self.b_memory_size, (self.id, 'B'))
        else:
            raise ValueError(f'del_virtual -> virtual id: {virtual_id}, server node error')


# class AServer(MyServer):
#     def __init__(self, genre, purchase_id):
#         super(AServer, self).__init__(genre, purchase_id)
#         self.a_contain = set()
#         self.node = 'A'
#
#     def add_virtual(self, virtual_id: str):
#         v = genre_to_market_virtual[id_to_virtual[virtual_id].genre]
#         self.a_contain.add(virtual_id)
#         self.a_core_num -= v.core_num
#         self.a_memory_size -= v.memory_size
#         if (self.a_core_num < 0) or (self.a_memory_size < 0):
#             raise ValueError(f"virtual_id: {virtual_id}, server_id: {self.id}")
#
#     def del_virtual(self, virtual_id: str, virtual_genre: str):
#         v = genre_to_market_virtual[id_to_virtual[virtual_id].genre]
#         self.a_contain.remove(virtual_id)
#         self.a_core_num += v.core_num
#         self.a_memory_size += v.memory_size
#
#
# class BServer(MyServer):
#     def __init__(self, genre, purchase_id):
#         super(BServer, self).__init__(genre, purchase_id)
#         self.b_contain = set()
#         self.node = 'B'
#
#     def add_virtual(self, virtual_id: str):
#         v = genre_to_market_virtual[id_to_virtual[virtual_id].genre]
#         self.b_contain.add(virtual_id)
#         self.b_core_num -= v.core_num
#         self.b_memory_size -= v.memory_size
#         if (self.b_core_num < 0) or (self.b_memory_size < 0):
#             raise ValueError(f"virtual_id: {virtual_id}, server_id: {self.id}")
#
#     def del_virtual(self, virtual_id: str, virtual_genre: str):
#         v = genre_to_market_virtual[id_to_virtual[virtual_id].genre]
#         self.b_contain.remove(virtual_id)
#         self.b_core_num += v.core_num
#         self.b_memory_size += v.memory_size
#
#
# class ABServer(MyServer):
#     def __init__(self, genre, purchase_id):
#         super(ABServer, self).__init__(genre, purchase_id)
#         self.contain = set()
#
#     def add_virtual(self, virtual_id: str):
#         v = genre_to_market_virtual[id_to_virtual[virtual_id].genre]
#         self.contain.add(virtual_id)
#         self.core_num -= v.core_num
#         self.memory_size -= v.memory_size
#         if (self.core_num < 0) or (self.memory_size < 0):
#             raise ValueError(f"virtual_id: {virtual_id}, server_id: {self.id}")
#
#     def del_virtual(self, virtual_id: str, virtual_genre: str):
#         v = genre_to_market_virtual[id_to_virtual[virtual_id].genre]
#         self.contain.remove(virtual_id)
#         self.core_num += v.core_num
#         self.memory_size += v.memory_size


def distribute_add(distribute: Dict[int, Dict[int, List]], core: int, memory: int, value):
    dc = distribute[core]
    if memory in dc:
        dc[memory].append(value)
    else:
        dc[memory] = [value]


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
            server = vc[various_memory[memory_start]][0]
    return server


def read_records():
    n = int(input())  # 可以采购的服务器类型数量, 1≤N≤100
    market_server_core_memory_distribute: Dict[int, Dict[int, List[str]]] = defaultdict(dict)
    for i in range(n):
        # (型号, CPU 核数, 内存大小, 硬件成本, 每日能耗成本)
        genre, core, memory, hardware, energy = input()[1:-1].split(', ')
        genre_to_market_server[genre] = Server(genre, int(core), int(memory), int(hardware), int(energy))
        mc = market_server_core_memory_distribute[int(core)]
        if int(memory) in mc:
            exist = mc[int(memory)][0]
            if genre_to_market_server[exist].hardware_cost > int(hardware):
                mc[int(memory)] = genre
        else:
            mc[int(memory)] = [genre]

    m = int(input())  # 售卖的虚拟机类型数量, 1≤M≤1000
    for i in range(m):
        # (型号, CPU 核数, 内存大小, 是否双节点部署)
        genre, core, memory, twin = input()[1:-1].split(', ')
        genre_to_market_virtual[genre] = Virtual(genre, int(core), int(memory), bool(int(twin)))

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
                if market_virtual.is_twin:
                    server_id = find_nearest_server(double_server_distribute, market_virtual)
                    if server_id:
                        server = purchase_id_to_server[server_id]
                    else:
                        # 买新服务器
                        new_server_genre = find_nearest_server(market_server_core_memory_distribute, market_virtual)
                        server = MyServer(new_server_genre, purchased_id)
                        purchase_id_to_server[purchased_id] = server
                        today_purchase[new_server_genre].append(server)
                        purchased_id += 1

                    id_to_virtual[virtual_id].server_id = server.id
                    id_to_virtual[virtual_id].server_node = 'AB'
                    deploy_design.append([virtual_id, server.id])
                    server.add_virtual(virtual_id)
                else:
                    migrate_info = find_nearest_server(single_server_distribute, market_virtual)
                    if migrate_info:
                        server = purchase_id_to_server[migrate_info[0]]
                        id_to_virtual[virtual_id].server_id = server.id
                        id_to_virtual[virtual_id].server_node = migrate_info[1]
                        deploy_design.append([virtual_id, server.id, migrate_info[1]])
                        server.add_virtual(virtual_id)
                    else:
                        single_virtual = Virtual(genre + '*2', market_virtual.core_num * 2, market_virtual.memory_size * 2, False)
                        new_server_genre = find_nearest_server(market_server_core_memory_distribute, single_virtual)
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

    # 实际的服务器和虚拟机
    purchase_id_to_server: Dict[int, MyServer] = {}
    id_to_virtual: Dict[str, MyVirtual] = {}
    # double_node_servers: List[DoubleServer] = []  # 从小到大排列，依次比较 核数 内存
    # single_node_servers: List[SingleServer] = []
    double_server_distribute: Dict[int, Dict[int, List[int]]] = defaultdict(dict)  # 用于接收双节点虚拟机
    single_server_distribute: Dict[int, Dict[int, List[tuple]]] = defaultdict(dict)  # 用于接收单节点虚拟机

    # purchase_output: List[str] = []
    deploy_design: List[List] = []
    expensive_server = ['', 0, 0]
    read_records()
