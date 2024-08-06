from functools import wraps
from asyncio import run, timeout
from time import perf_counter
from math import isclose
from pyglicko2 import Player, system, WIN, LOSS

class test:
    n = 0
    tests = []

    def __init__(self, name=None, times=1, timeout=1):
        test.n += 1
        self._id, self.times, self.timeout, self.name = test.n, times, timeout, name

    def __call__(self, f):
        @wraps(f)
        async def wrapper():
            print(end=f'Test #{self._id}{f' ()' if self.name else ''}: ')
            try:
                st = perf_counter()
                for _ in range(self.times):
                    async with timeout(self.timeout):
                        await f()
                print(f'Passed in {perf_counter() - st:.3f}s')
                return 0
            except TimeoutError:
                print('Failed: Timed Out')
                return 1
            except Exception as e:
                print(f'Failed: ({type(e)}) {e}')
                return 1
        test.tests.append(wrapper)
        return wrapper
    
    @classmethod
    async def execute_all(cls):
        s = cls.n
        for t in cls.tests:
            s -= await t()
        print(f'Passed {s}/{cls.n}')

@test()
async def simple_test():
    with system(.5):
        player1 = Player(RD=200)
        player2 = Player(1400, 30)
        player3 = Player(1550, 100)
        player4 = Player(1700, 300)
        player1.update([player2, player3, player4], [WIN, LOSS, LOSS])
        assert isclose(player1.r, 1464.0506705393013)
        assert isclose(player1.RD, 151.51652412385727)
        assert isclose(player1.σ, 0.059995984286488495)

run(test.execute_all())