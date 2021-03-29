from collections import defaultdict
from bisect import bisect_left
from typing import Dict, List


class Resource:
    def __init__(self, core, memory):
        self.core_num = core
        self.memory_size = memory
        self.memory_core_rate = memory / core

    def __lt__(self, other):
        # 存核比 核数 内存，依次比较
        # if self.memory_core_rate == other.memory_core_rate:
        #     if self.core_num == other.core_num:
        #         return self.memory_size < other.memory_size
        #     else:
        #         return self.core_num < other.core_num
        # else:
        #     return self.memory_core_rate < other.memory_core_rate

        if self.core_num == other.core_num:
            return self.memory_size < other.memory_size
        else:
            return self.core_num < other.core_num


class Server(Resource):
    def __init__(self, genre: str, core: int, memory: int, hardware: int, energy: int):
        super(Server, self).__init__(core, memory)
        self.genre = genre  # 长度不超过 20
        # self.core_num = core  # 不超过 1024
        # self.memory_size = memory  # 不超过 1024
        # self.memory_core_rate = memory / core
        self.hardware_cost = hardware  # 不超过 5 × 10^5
        self.energy_cost = energy  # 不超过 5000
        self.a_core_num = self.b_core_num = core // 2
        self.a_memory_size = self.b_memory_size = memory // 2

    def __str__(self):
        return f'(型号: {self.genre}, CPU核数: {self.core_num}, 内存大小: {self.memory_size}, ' \
               f'存核比: {self.memory_core_rate}, 硬件成本: {self.hardware_cost}, 每日能耗成本: {self.energy_cost})'


class Virtual(Resource):
    # 对于每种类型的虚拟机，数据集保证至少存在一种服务器可以容纳
    def __init__(self, genre: str, core: int, memory: int, twin: bool):
        super(Virtual, self).__init__(core, memory)
        self.genre = genre  # 长度不超过 20
        # self.core_num = core  # 不超过 1024
        # self.memory_size = memory  # 不超过 1024
        # self.memory_core_rate = memory / core
        self.is_twin = twin  # 不超过 5 × 10^5

    def __str__(self):
        return f'(型号: {self.genre}, CPU核数: {self.core_num}, ' \
               f'内存大小: {self.memory_size}, 是否双节点: {self.is_twin})'


class MyVirtual:
    def __init__(self, genre: str, request_id: str):
        v = genre_to_market_virtual[genre]
        # super(MyVirtual, self).__init__(v.core_num, v.memory_size)
        # 实际上可以不继承 Resource，虚拟机的资源占用是固定的，可以通过字典去查
        # 比较大小的时候就得查了再比，继承了就省得麻烦

        self.genre = genre
        self.id = request_id  # 读出来的时候是字符串，就没做转换
        self.server_id = -1
        self.server_node = 'Z'

    # def migrate(self, destination, node):
    #     self.server_id = destination
    #     self.server_node = node
    #
    #     if node == 'A':
    #         pass


class MyServer(Resource):
    def __init__(self, genre: str, purchase_id: int):
        self.genre = genre
        self.id = purchase_id
        self.output_id = -1

        # 余量还有多少
        s = genre_to_market_server[genre]
        super(MyServer, self).__init__(s.core_num, s.memory_size)
        self.a_core_num = s.a_core_num
        self.a_memory_size = s.a_memory_size
        self.a_memory_core_rate = self.a_memory_size / self.a_core_num
        self.b_core_num = s.b_core_num
        self.b_memory_size = s.b_memory_size
        self.b_memory_core_rate = self.b_memory_size / self.b_core_num

        # self.memory_size = self.a_memory_size + self.b_memory_size
        # self.core_num = self.a_core_num + self.b_core_num
        # self.memory_core_rate = self.memory_size / self.core_num
        # self.update_cm_rate()

    def update_cm_rate(self):
        if self.a_core_num > 0:
            self.a_memory_core_rate = self.a_memory_size / self.a_core_num
        if self.b_core_num > 0:
            self.b_memory_core_rate = self.b_memory_size / self.b_core_num
        if self.core_num > 0:
            self.memory_core_rate = self.memory_size / self.core_num

    def add_virtual(self, *args):
        raise ValueError("add_virtual needs to be implemented by subclass")

    def del_virtual(self, *args):
        raise ValueError("del_virtual needs to be implemented by subclass")


class SingleServer(MyServer):
    # 只分配给 单节点 的虚拟机使用
    def __init__(self, genre: str, purchase_id: int):
        super(SingleServer, self).__init__(genre, purchase_id)
        self.a_contain = set()
        self.b_contain = set()
        self.memory_core_for_single()

    def memory_core_for_single(self):
        if (self.b_core_num >= self.a_core_num) and (self.b_memory_size >= self.a_memory_size):
            self.memory_size = self.b_memory_size
            self.core_num = self.b_core_num
        elif (self.b_core_num <= self.a_core_num) and (self.b_memory_size <= self.a_memory_size):
            self.memory_size = self.a_memory_size
            self.core_num = self.a_core_num
        else:
            self.memory_size = min(self.a_memory_size, self.b_memory_size)
            self.core_num = min(self.a_core_num, self.b_core_num)

    def add_virtual(self, virtual_id: str, virtual_genre: str, node: str):
        v = genre_to_market_virtual[virtual_genre]
        if node == 'A':
            self.a_contain.add(virtual_id)
            self.a_core_num -= v.core_num
            self.a_memory_size -= v.memory_size
            if (self.a_core_num < 0) or (self.a_memory_size < 0):
                raise ValueError(f"virtual_id: {virtual_id}, server_id: {self.id}, node: {node}")
        elif node == 'B':
            self.b_contain.add(virtual_id)
            self.b_core_num -= v.core_num
            self.b_memory_size -= v.memory_size
            if (self.b_core_num < 0) or (self.b_memory_size < 0):
                raise ValueError(f"virtual_id: {virtual_id}, server_id: {self.id}, node: {node}")
        elif node == 'AB':
            # 对于 SingleServer 来说，该情况暂时不存在
            self.a_contain.add(virtual_id)
            self.a_core_num -= v.core_num // 2
            self.a_memory_size -= v.memory_size // 2
            self.b_contain.add(virtual_id)
            self.b_core_num -= v.core_num // 2
            self.b_memory_size -= v.memory_size // 2
        self.memory_core_for_single()

    def del_virtual(self, virtual_id: str, virtual_genre: str, node: str):
        v = genre_to_market_virtual[virtual_genre]
        if node == 'A':
            self.a_contain.remove(virtual_id)
            self.a_core_num += v.core_num
            self.a_memory_size += v.memory_size
        elif node == 'B':
            self.b_contain.remove(virtual_id)
            self.b_core_num += v.core_num
            self.b_memory_size += v.memory_size
        elif node == 'AB':
            self.a_contain.remove(virtual_id)
            self.a_core_num += v.core_num // 2
            self.a_memory_size += v.memory_size // 2
            self.b_contain.remove(virtual_id)
            self.b_core_num += v.core_num // 2
            self.b_memory_size += v.memory_size // 2
        self.memory_core_for_single()


class DoubleServer(MyServer):
    # A B 节点的资源分配保持一致，它只分配给 双节点 的虚拟机使用
    def __init__(self, genre: str, purchase_id: int):
        super(DoubleServer, self).__init__(genre, purchase_id)
        self.contain = set()

    def add_virtual(self, virtual_id: str, virtual_genre: str, node='AB'):
        self.contain.add(virtual_id)
        v = genre_to_market_virtual[virtual_genre]
        self.memory_size -= v.memory_size
        self.core_num -= v.core_num
        self.a_memory_size -= v.memory_size // 2
        self.a_core_num -= v.core_num // 2
        self.b_memory_size -= v.memory_size // 2
        self.b_core_num -= v.core_num // 2

        if (self.a_core_num < 0) or (self.a_memory_size < 0) or (self.b_core_num < 0) or (self.b_memory_size < 0):
            raise ValueError(f"virtual_id: {virtual_id}, server_id: {self.id}, node: {node}")
        # self.update_cm_rate()

    def del_virtual(self, virtual_id: str, virtual_genre: str, node='AB'):
        self.contain.remove(virtual_id)
        v = genre_to_market_virtual[virtual_genre]
        self.memory_size += v.memory_size
        self.core_num += v.core_num
        self.a_memory_size += v.memory_size // 2
        self.a_core_num += v.core_num // 2
        self.b_memory_size += v.memory_size // 2
        self.b_core_num += v.core_num // 2
        # self.update_cm_rate()


# def migrate(server_position, virtual_id, servers, node='AB'):
#     server = servers.pop(server_position)
#     server.add_virtual(virtual_id, id_to_virtual[virtual_id].genre, node)
#     if node == 'AB':
#         deploy_design.append([virtual_id, server.id])  # 输出迁移记录f'({virtual_id}, {server.id})'
#     else:
#         deploy_design.append([virtual_id, server.id, node])
#     id_to_virtual[virtual_id].server_node = node
#     id_to_virtual[virtual_id].server_id = server.id
#     servers.insert(bisect_left(servers, server), server)


def migrate(server_id: int, virtual_id: str, node='AB'):
    server = purchase_id_to_server[server_id]
    if node == 'AB':
        double_node_servers_distribute[server.core_num][server.memory_size].remove(server_id)
        server.add_virtual(virtual_id, id_to_virtual[virtual_id].genre, node)
        deploy_design.append([virtual_id, server_id])  # 输出迁移记录f'({virtual_id}, {server.id})'
        sc = double_node_servers_distribute[server.core_num]
        if server.memory_size in sc:
            sc[server.memory_size].append(server_id)
        else:
            sc[server.memory_size] = [server_id]
    else:
        single_node_servers_distribute[server.core_num][server.memory_size].remove(server_id)
        server.add_virtual(virtual_id, id_to_virtual[virtual_id].genre, node)
        deploy_design.append([virtual_id, server_id, node])
        sc = single_node_servers_distribute[server.core_num]
        if server.memory_size in sc:
            sc[server.memory_size].append(server_id)
        else:
            sc[server.memory_size] = [server_id]

    id_to_virtual[virtual_id].server_node = node
    id_to_virtual[virtual_id].server_id = server_id


# def delete(server_id, virtual_id, servers, node='AB'):
#     server = purchase_id_to_server[server_id]
#     servers.remove(server)  # 可用二分
#     server.del_virtual(virtual_id, id_to_virtual[virtual_id].genre, node)
#     servers.insert(bisect_left(servers, server), server)


def delete(server_id, virtual_id, node='AB'):
    server = purchase_id_to_server[server_id]
    if node == 'AB':
        distribute = double_node_servers_distribute
    else:
        distribute = single_node_servers_distribute

    distribute[server.core_num][server.memory_size].remove(server_id)
    server.del_virtual(virtual_id, id_to_virtual[virtual_id].genre, node)
    sc = distribute[server.core_num]
    if server.memory_size in sc:
        sc[server.memory_size].append(server_id)
    else:
        sc[server.memory_size] = [server_id]


def find_nearest_server(distribution: Dict, virtual: Virtual, purchase=True):
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
        # dis = (various_memory[memory_start] - virtual.memory_size) + (various_core[core] - virtual.core_num)
        # if purchase:
        #     for memory in range(memory_start, len(various_memory)):
        #         for genre in vc[various_memory[memory]]:
        #             hardware = genre_to_market_server[genre].hardware_cost
        #             if hardware < distance:
        #                 distance = hardware
        #                 server = genre
        #     # server = expensive_server[0]
        # else:
        dis = (various_memory[memory_start] - virtual.memory_size) ** 2 + \
              (various_core[core] - virtual.core_num) ** 2
        if dis < distance:
            distance = dis
            server = vc[various_memory[memory_start]][0]
    return server


def read_records():
    n = int(input())  # 可以采购的服务器类型数量, 1≤N≤100
    market_server_core_memory_distribute: Dict[int, Dict[int, List[str]]] = defaultdict(dict)
    mc = 0
    for i in range(n):
        # (型号, CPU 核数, 内存大小, 硬件成本, 每日能耗成本)
        genre, core, memory, hardware, energy = input()[1:-1].split(', ')
        # rate = 2
        # if (1 / rate) <= (int(memory) / int(core)) <= rate:
        if int(core) * int(memory) > mc:
            mc = int(core) * int(memory)
            expensive_server[0] = genre
            expensive_server[1] = int(hardware)
            expensive_server[2] = int(energy)
        genre_to_market_server[genre] = Server(genre, int(core), int(memory), int(hardware), int(energy))
        if int(memory) in market_server_core_memory_distribute[int(core)]:
            market_server_core_memory_distribute[int(core)][int(memory)].append(genre)
        else:
            market_server_core_memory_distribute[int(core)][int(memory)] = [genre]
        # print(genre_to_market_server[genre])
    # market_server_sort = sorted(list(genre_to_market_server.values()),
    #                             key=lambda x: (x.core_num, x.memory_size, x.hardware_cost, x.energy_cost))

    m = int(input())  # 售卖的虚拟机类型数量, 1≤M≤1000
    for i in range(m):
        # (型号, CPU 核数, 内存大小, 是否双节点部署)
        genre, core, memory, twin = input()[1:-1].split(', ')
        genre_to_market_virtual[genre] = Virtual(genre, int(core), int(memory), bool(int(twin)))
        # print(genre_to_market_virtual[genre])

    t = int(input())  # T 天的用户请求序列数据, 1≤T≤1000
    purchased_id, actual_id = 0, 0
    for i in range(t):
        r = int(input())  # 当天共有 R 条请求, 用户创建请求数量总数不超过 10^5
        today_purchase = defaultdict(list)
        for j in range(r):
            # (add, 虚拟机型号, 虚拟机 ID) 或 (del, 虚拟机 ID)
            request = input()[1:-1].split(', ')

            if request[0] == 'add':
                _, genre, virtual_id = request
                id_to_virtual[virtual_id] = MyVirtual(genre, virtual_id)
                virtual = genre_to_market_virtual[genre]
                if virtual.is_twin:
                    server_id = find_nearest_server(double_node_servers_distribute, virtual, purchase=False)
                    if server_id:
                        server = purchase_id_to_server[server_id]
                    else:
                        # 买新服务器
                        new_server_genre = find_nearest_server(market_server_core_memory_distribute, virtual)
                        server = DoubleServer(new_server_genre, purchased_id)
                        sc = double_node_servers_distribute[server.core_num]
                        if server.memory_size in sc:
                            sc[server.memory_size].append(server.id)
                        else:
                            sc[server.memory_size] = [server.id]
                        purchase_id_to_server[purchased_id] = server
                        today_purchase[new_server_genre].append(server)
                        purchased_id += 1

                    migrate(server.id, virtual_id)
                else:
                    server_id = find_nearest_server(single_node_servers_distribute, virtual, purchase=False)
                    if server_id:
                        server = purchase_id_to_server[server_id]
                    else:
                        single_virtual = Virtual(genre + '*2', virtual.core_num * 2, virtual.memory_size * 2, False)
                        new_server_genre = find_nearest_server(market_server_core_memory_distribute, single_virtual)
                        server = SingleServer(new_server_genre, purchased_id)
                        sc = single_node_servers_distribute[server.core_num]
                        if server.memory_size in sc:
                            sc[server.memory_size].append(server.id)
                        else:
                            sc[server.memory_size] = [server.id]
                        purchase_id_to_server[purchased_id] = server
                        today_purchase[new_server_genre].append(server)
                        purchased_id += 1

                    if (server.a_core_num >= virtual.core_num) and (server.a_memory_size >= virtual.memory_size):
                        migrate(server.id, virtual_id, 'A')
                    else:
                        migrate(server.id, virtual_id, 'B')
            else:
                _, virtual_id = request
                v = id_to_virtual[virtual_id]
                if genre_to_market_virtual[v.genre].is_twin:
                    delete(id_to_virtual[virtual_id].server_id, virtual_id)
                else:
                    delete(id_to_virtual[virtual_id].server_id, virtual_id, v.server_node)

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
    double_node_servers_distribute: Dict[int, Dict[int, List[int]]] = defaultdict(dict)  # 只接收双节点虚拟机
    single_node_servers_distribute: Dict[int, Dict[int, List[int]]] = defaultdict(dict)  # 只接收单节点虚拟机

    # purchase_output: List[str] = []
    deploy_design: List[List] = []
    expensive_server = ['', 0, 0]
    read_records()
