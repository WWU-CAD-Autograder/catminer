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
        @catminer.timer(file_name="foo")
        def waste_time():
            for i in range(10000):
                continue

        start_time = time.perf_counter()
        waste_time()
        end_time = time.perf_counter()

        path = os.path.join(self.path, r'.\out\catminer.log')
        with open(path, 'r') as f:
            text = f.read()

        expected = end_time - start_time
        measured = float(re.findall(r"\d+\.\d+(?= seconds)", text)[0])
        self.assertAlmostEqual(expected, measured, 2)

    def test_get_path(self):
        rel_path = r'..\tests\out'
        path = catminer.get_path(rel_path)
        self.assertTrue(os.path.exists(path))


class TestMiner(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ...
