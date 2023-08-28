import multiprocessing
from concurrent.futures import ProcessPoolExecutor


def put_in_q(q, x):
    q.put(x)


class TestClass:

    N: int = 10

    def test_method(self):
        print("Running test method...")
        process_count = multiprocessing.cpu_count()
        manager = multiprocessing.Manager()
        queue = manager.Queue()

        with ProcessPoolExecutor(max_workers=process_count) as executor:
            executor.map(put_in_q, [queue] * self.N, range(self.N))

        while not queue.empty():
            print(queue.get())


if __name__ == "__main__":
    obj = TestClass()
    obj.test_method()
