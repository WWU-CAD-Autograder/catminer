import logging
import os
import pyvba
import re
import sys
import time
import traceback
import zipfile as zf
from enum import IntEnum

TYPE_RE = re.compile(r'(?<=\.CAT)[^.]*?$')
FILE_RE = re.compile(r'[^\\]+?(?=\.CAT)')
DIR_PATH = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.NOTSET,
    filename=os.path.join(DIR_PATH, r'..\tests\out\catminer.log'),
    filemode='w'
)


def timer(task: str):
    """Wrapper function to time the function execution time."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            text = f"Started {task}."
            print(text)
            logger.info(text)

            output = func(*args, **kwargs)
            end_time = time.perf_counter()

            text = f"Finished {task} in {(end_time - start_time):.4f} seconds."
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
        self._path = os.path.abspath(path) if path is not None else os.path.join(DIR_PATH, r"..\input")
        self._out_dir = os.path.abspath(out_dir) if out_dir is not None else os.path.join(DIR_PATH, r"..\output")
        self._file_type = file_type.value
        self._start_time = time.perf_counter()

        # change logger properties
        global logger

        fh = logging.FileHandler(os.path.join(self._out_dir, r'catminer.log'), 'w')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.setLevel(logging.INFO)

    def begin(self) -> None:
        """Commence the data-mining process once setting are in place, if applicable."""
        _update_log('---------------BEGIN EXPORT---------------')

        try:
            self._dir_crawl(self._path, self._out_dir)
        except BaseException:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            [
                logger.critical(re.sub(r'(\n| {2,})', '', str(i)))
                for i in traceback.format_exception(exc_type, exc_value, exc_traceback)
            ]
            time.sleep(0.1)
            traceback.print_exception(exc_type, exc_value, exc_traceback)

    def _dir_crawl(self, path: str, out_dir: str) -> None:
        """Crawl through, process, and duplicate the directory.

        This function is tasked to iterating through the directory tree. If a CATIA file is encountered, an export
        process will be launched. If a zip file is encountered, it will be opened and the crawl will proceed. If a
        folder is encountered, it will be duplicated in the respective output folder.
        """
        for file in os.listdir(path):
            file_path = os.path.join(path, file)

            # directory found -> scan it
            if os.path.isdir(file_path):
                dir_path = os.path.join(out_dir, file)

                if not os.path.exists(dir_path):
                    _update_log(f'Created path: {dir_path}.')
                    os.mkdir(dir_path)

                self._dir_crawl(file_path, dir_path)

            # file found
            elif os.path.isfile(file_path):
                # zipfile found -> unzip it and scan it
                if zf.is_zipfile(file_path):
                    with zf.ZipFile(file_path) as zfile:
                        file_name = re.findall(r'(?<=\\)[^\\]+?(?=\.zip)', zfile.filename)[0]
                        new_out_dir = os.path.join(out_dir, file_name)
                        new_path = os.path.join(path, file_name)

                        if not os.path.exists(new_out_dir):
                            _update_log(f'Created path: {new_out_dir}.')
                            os.mkdir(new_out_dir)
                        if not os.path.exists(new_path):
                            _update_log(f'Created path: {new_path}.')
                            os.mkdir(new_path)

                        zfile.extractall(new_path)
                        self._dir_crawl(new_path, new_out_dir)

                # CATIA file found
                elif TYPE_RE.search(file_path):
                    self._export_file(os.path.join(path, file), out_dir)

    def _cat_type(self, cat_file: str) -> pyvba.Browser:
        """Return the browser object that correlates to the CATIA file being processed.

        Parameters
        ----------
        cat_file: str
            The CATIA.ActiveDocument.Name (i.e. the name of the file).

        Returns
        -------
        pyvba.Browser
            The VBA object that represents the correlated file type.

        Notes
        -----
        If the file doesn't open, wait for it to.
        """
        browser = pyvba.Browser("CATIA.Application")

        # ensure that the file is open
        try:
            file_type = TYPE_RE.findall(cat_file)[0]

            # get the right CATIA object
            if file_type == "Product":
                browser = browser.ActiveDocument.Product
            elif file_type == "Part":
                browser = browser.ActiveDocument.Part
            elif file_type == "Drawing":
                browser = browser.ActiveDocument.DrawingRoot
            elif file_type == "Process":
                browser = browser.ActiveDocument.PPRDocument
            else:
                browser = browser.ActiveDocument
        except AttributeError:
            # wait and try again
            time.sleep(1)
            self._cat_type(cat_file)

        return browser

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
        file_name = FILE_RE.findall(path)[0]
        file_type = TYPE_RE.findall(path)[0]

        # open the file
        _update_log(f"Opening \"{file_name + '.CAT' + file_type}\".")
        opened_file = self.browser.Documents.Open(path)
        browser = self._cat_type(path)

        # select the right exporter
        if self._file_type == 1:
            exporter = pyvba.JSONExport(browser, skip_func=True, skip_err=True)
        else:
            exporter = pyvba.XMLExport(browser, skip_func=True, skip_err=True)

        # export the file and start a timer
        timer(f"export for \"{file_name + '.CAT' + file_type}\"")(exporter.save)(file_name, out_dir)

        # ensure that the file closes
        opened_file.Close()
        time.sleep(1)

    def _finish(self) -> None:
        """Cleans up any open files."""
        self.browser = None
        total_time = self._start_time - time.perf_counter()
        _update_log(f"Finished batch export in {total_time:.4f}.")


if __name__ == "__main__":
    CATMiner(r"..\input", r"..\output").begin()
