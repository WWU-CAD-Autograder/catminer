import argparse
import logging
import os
import pyvba
import re
import time
import zipfile as zf

from enum import IntEnum

TYPE_RE = re.compile(r'(?<=\.CAT)[^.]*?$')
FILE_RE = re.compile(r'[^\\]+?(?=\.CAT)')
DIR_PATH = os.path.dirname(__file__)

logger = logging.getLogger('catminer')
logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.NOTSET,
    filename=os.path.join(DIR_PATH, r'..\tests\out\catminer.log'),
    filemode='w'
)


def timer(file_name: str):
    """Wrapper function to time the function execution time."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            text = f"Started export for {file_name}."
            print(text)
            logger.info(text)

            output = func(*args, **kwargs)
            end_time = time.perf_counter()

            text = f"Finished export for {file_name} in {(end_time - start_time):.4f} seconds."
            print(text)
            logger.info(text)

            return output
        return wrapper
    return decorator


def get_path(rel_path: str) -> str:
    """Returns the complete path given a relative one.

    Parameters
    ----------
    rel_path: str
        The relative path of the file.

    Returns
    -------
    str
        The complete path of the file.
    """
    return os.path.join(DIR_PATH, rel_path)


def _update_log(text: str, level: int = logging.INFO) -> None:
    """Add an entry to the log and print out step."""
    logger.log(level, text)
    print(text)


class FileType(IntEnum):
    """Enumerator that holds the files types."""
    XML = 0
    JSON = 1


class CATMiner:
    def __init__(self, path: str = None, out_dir: str = None, file_type: IntEnum = FileType.XML, **kwargs):
        """The CATMiner class is used to extract data in a batch process.

        Parameters
        ----------
        path: str
            The input path.
        out_dir: str
            The output path.
        """
        self.browser = pyvba.Browser(kwargs.get('app', 'CATIA.Application'))
        self._path = path if path is not None else os.path.join(DIR_PATH, r"..\input")
        self._out_dir = out_dir if out_dir is not None else os.path.join(DIR_PATH, r"..\output")
        self._file_type = file_type.value
        self._start_time = time.perf_counter()

        # change logger save location
        logger.removeHandler('catminer')
        logger.addHandler(
            logging.FileHandler(
                os.path.join(self._out_dir, r'catminer.log'), 'w'
            )
        )

    def begin(self) -> None:
        """Commence the data-mining process once setting are in place, if applicable."""
        self._dir_crawl(self._path, self._out_dir)

    def _dir_crawl(self, path: str, out_dir: str) -> None:
        """Crawl through, process, and duplicate the directory.

        This function is tasked to iterating through the directory tree. If a CATIA file is encountered, an export
        process will be launched. If a zip file is encountered, it will be opened and the crawl will proceed. If a
        folder is encountered, it will be duplicated in the respective output folder.
        """
        for f in os.listdir(path):
            if os.path.isdir(f):
                dir_path = os.path.join(out_dir, f)

                if not os.path.exists(dir_path):
                    _update_log(f'Created path: {dir_path}.')
                    os.mkdir(dir_path)
            elif os.path.isfile(f):
                if zf.is_zipfile(f):
                    with zf.ZipFile(f) as zfile:
                        new_out_dir = os.path.join(out_dir, zfile.filename)
                        new_path = os.path.join(path, zfile.filename)

                        if not os.path.exists(new_out_dir):
                            _update_log(f'Created path: {new_out_dir}.')
                            os.mkdir(new_out_dir)
                        if not os.path.exists(new_path):
                            _update_log(f'Created path: {new_path}.')
                            os.mkdir(new_path)

                        zfile.extractall(new_path)
                        self._dir_crawl(new_path, new_out_dir)
                if TYPE_RE.match(f):
                    self._export_file(os.path.join(path, f), out_dir)

    def _cat_type(self, cat_file_type: str) -> pyvba.Browser:
        """Return the browser object that correlates to the CATIA file being processed.

        Parameters
        ----------
        cat_file_type: str
            The CATIA.ActiveDocument.Name (i.e. the name of the file).

        Returns
        -------
        pyvba.Browser
            The VBA object that represents the correlated file type.
        """
        file_type = TYPE_RE.findall(cat_file_type)[0]

        if file_type == "Product":
            return self.browser.ActiveDocument.Product
        elif file_type == "Part":
            return self.browser.ActiveDocument.Part
        elif file_type == "Drawing":
            return self.browser.ActiveDocument.DrawingRoot
        elif file_type == "Process":
            return self.browser.ActiveDocument.PPRDocument

        return self.browser.ActiveDocument

    def _export_file(self, path: str, out_dir: str) -> None:
        """Exports a CATIA file to a specified location using pyvba.

        Parameters
        ----------
        path: str
            The path of the file.
        out_dir: str
            The output path for the exported file.

        Notes
        -----
        The document is opened in CATIA then closed when finished. Errors are logged.
        """
        browser = self._cat_type(path)
        file_name = FILE_RE.findall(path)[0]
        file_type = TYPE_RE.findall(path)[0]

        if self._file_type == 1:
            exporter = pyvba.JSONExport(browser, skip_func=True, skip_err=True)
        else:
            exporter = pyvba.XMLExport(browser, skip_func=True, skip_err=True)

        timer(file_name + '.CAT' + file_type)(exporter.save)(file_name, out_dir)

    def _finish(self) -> None:
        """Cleans up any open files."""
        self.browser = None
        total_time = self._start_time - time.perf_counter()
        _update_log(f"Finished batch export in {total_time:.4f}.")


if __name__ == "__main__":
    ...
