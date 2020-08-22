import argparse
import logging
import os
import pyvba
import re
import time
import zipfile

browser = pyvba.Browser('CATIA.Application')
print(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)-8s %(message)s',
    filename=r'..\output\catminer.log',
    filemode='w', level=logging.NOTSET
)


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()

        text = f"Started {func.__name__!r}."
        print(text)
        logger.info(text)

        output = func(*args, **kwargs)
        end_time = time.perf_counter()

        text = f"Finished {func.__name__!r} in {(end_time - start_time):.4f} seconds."
        print(text)
        logger.info(text)

        return output
    return wrapper


class Miner:
    def __init__(self, path: str = None, out_dir: str = None): ...

    def begin(self) -> None: ...

    def _update_log(self) -> None: ...

    def _dir_crawl(self) -> None: ...

    def _create_folder(self, name: str, path: str) -> None: ...

    def _open_zip(self, path: str) -> list: ...

    @staticmethod
    def cat_type(cat_file_name: str) -> pyvba.Browser: ...

    def _export_file(self, path: str) -> None: ...

    def _finish(self) -> None: ...


if __name__ == "__main__":
    ...
