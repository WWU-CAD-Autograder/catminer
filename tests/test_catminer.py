import os
import re
import time
import unittest
import logging

import catminer


class TestExternalFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = os.path.dirname(__file__)
        cls.out_path = os.path.abspath(r'.\out')
        cls.log_path = os.path.abspath(os.path.join(cls.out_path, 'catminer.log'))

        if not os.path.exists(cls.out_path):
            os.makedirs(os.path.abspath(cls.out_path))
        elif os.path.exists(cls.log_path):
            os.remove(cls.log_path)

        logger = catminer.catminer.logger
        [logger.removeHandler(i) for i in logger.handlers]

        fh = logging.FileHandler(cls.log_path, 'w')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.setLevel(logging.INFO)
        logging.info('----BEGIN TESTS----')

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
        with open(self.log_path, 'r') as f:
            text = f.read()

        # compare
        expected = end_time - start_time
        measured = float(re.findall(r"\d+\.\d+(?= seconds)", text)[0])
        self.assertAlmostEqual(expected, measured, 2)
