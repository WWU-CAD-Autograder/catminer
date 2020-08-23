import os
import re
import time
import unittest

import catminer


class TestExternalFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = os.path.dirname(__file__)

    def test_timer(self):
        # test function
        @catminer.timer(task="wasting time")
        def waste_time():
            for i in range(10000):
                continue

        # get actual time
        start_time = time.perf_counter()
        waste_time()
        end_time = time.perf_counter()

        # open and read the log output
        path = os.path.join(self.path, r'.\out\catminer.log')
        with open(path, 'r') as f:
            text = f.read()

        # compare
        expected = end_time - start_time
        measured = float(re.findall(r"\d+\.\d+(?= seconds)", text)[0])
        self.assertAlmostEqual(expected, measured, 2)

    def test_get_path(self):
        # test that the path exists
        rel_path = r'..\tests\out'
        path = catminer.get_path(rel_path)
        self.assertTrue(os.path.exists(path))


class TestMiner(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ...
