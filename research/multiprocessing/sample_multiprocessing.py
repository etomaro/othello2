import multiprocessing

def f(x):
    print(f"{x}: x")
    return x * x

if __name__ == '__main__':
    cpu_count = num_cores = multiprocessing.cpu_count()
    with multiprocessing.Pool(5) as p:
        print("並列化スタート")
        result = p.map(f, range(1000000))
        print(f"len(result): {len(result)}")
        print("並列化エンド")
        # print(f"result: {result}")