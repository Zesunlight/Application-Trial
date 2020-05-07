from collections import defaultdict
import multiprocessing as mp


def cycle(point, path, stream, trace_point):
    if len(path) >= 7:
        return 0

    path.append(point)
    for next_point in stream[point]:
        if next_point == path[0] and len(path) >= 3:
            if min(path) == path[0]:
                trace_point[len(path) - 3].append(','.join([str(x) for x in path]))
            # print(','.join([str(x) for x in path]))
        elif next_point in path:
            continue
        else:
            cycle(next_point, path.copy(), stream, trace_point)
    # print('***************')
    # print(trace_point)
    # print('***************')
    return trace_point


def cycle_wrap(begin_keys, stream):
    trace_wrap = [[], [], [], [], []]
    for begin in begin_keys:
        trace_point = cycle(begin, [], stream, [[], [], [], [], []])
        stream[begin] = []
        for i in range(5):
            trace_wrap[i].extend(trace_point[i])
    # print('------------')
    # print(trace_wrap)
    # print('------------')
    return trace_wrap


def cycle_multi():
    num_of_process = 32
    chunk_size = len(start_keys) // num_of_process + 1
    process = []

    pool = mp.Pool(num_of_process)
    for i in range(num_of_process):
        process.append(pool.apply_async(cycle_wrap,
                                        args=(start_keys[i * chunk_size: (i + 1) * chunk_size], stream,)))
    pool.close()
    pool.join()

    trace_multi = [[], [], [], [], []]
    for p in process:
        trace_wrap = p.get()
        for i in range(5):
            trace_multi[i].extend(trace_wrap[i])
    return trace_multi


if __name__ == '__main__':
    stream = defaultdict(list)
    # trace = [[], [], [], [], []]

    data_path = '/data/test_data.txt'
    # data_path = r'C:\Users\DF\Desktop\TestData\3738\test_data.txt'
    with open(data_path, 'r') as account:
        for line in account:
            giver, receiver, _ = line.split(',')
            stream[int(giver)].append(int(receiver))
    # print('load data finish')

    start_keys = sorted(list(stream.keys()))
    for item in start_keys:
        stream[item].sort()
    # print('sort stream finish')

    # for start in start_keys:
    #     cycle(start, [])
    #     stream[start] = []
    # print('find cycles finish')
    trace = cycle_multi()

    sum = 0
    for item in trace:
        sum += len(item)
    # print(sum)

    result_path = '/projects/student/result.txt'
    # result_path = r'C:\Users\DF\Desktop\TestData\3738\result_self_multi.txt'
    with open(result_path, 'w') as result:
        result.write(str(sum) + '\n')
        for item in trace:
            for i in item:
                result.write(i + '\n')
