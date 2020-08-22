import unittest
import catminer
import time
import re


class TestTimer(unittest.TestCase):
    def test_timer(self):
        @catminer.timer
        def waste_time():
            for i in range(10000):
                continue

        start_time = time.perf_counter()
        waste_time()
        end_time = time.perf_counter()

        with open(r'..\output\catminer.log', 'r') as f:
            text = f.read()

        expected = end_time - start_time
        measured = float(re.findall(r"\d+\.\d+(?= seconds)", text)[0])
        self.assertAlmostEqual(expected, measured, 3)


class TestMiner(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ...
