import logging
import os
import pyvba
import re
import shutil
import sys
import textwrap
import time
import traceback
import zipfile as zf
from datetime import datetime
from io import BytesIO

from tqdm import tqdm

# define regular expressions
type_re = re.compile(r'(?<=\.CAT)[^.]*?$')
file_re = re.compile(r'[^\\/]+(?=\.)')

# define stub vars
XML = 0
JSON = 1

logger = logging.getLogger()


def timer(task: str):
    """Wrapper function to time the function execution time."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            text = f"Started {task}."
            logger.info(text)

            output = func(*args, **kwargs)
            end_time = time.perf_counter()

            text = f"Finished {task} in {(end_time - start_time):.4f} seconds."
            logger.info(text)

            return output

        return wrapper

    return decorator


def cat_file_list(path: str) -> list:
    """Return a list of all CATIA (.CAT*) files in the directory."""
    cats = []

    def process_zip(zipfile: zf.ZipFile):
        """Add all .CAT* files in the zipfile."""
        nonlocal cats

        for name in zipfile.namelist():
            data = BytesIO(zipfile.read(name))

            if '.CAT' in name:
                cats.append(file_re.findall(name)[0] + '.CAT' + type_re.findall(name)[0])
            elif zf.is_zipfile(data):
                with zf.ZipFile(data, 'r') as z:
                    process_zip(z)

    for dirpath, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(dirpath, file)

            if '.CAT' in file:
                cats.append(file)
            elif zf.is_zipfile(file_path):
                with zf.ZipFile(file_path, 'r') as z:
                    process_zip(z)

    return cats


def cat_in_dir(path: str) -> bool:
    """Returns true if a CATIA (.CAT*) files exists in the directory."""
    return any(cat_file_list(path))


class TQDMStreamHandler(logging.StreamHandler):
    """Class that overwrites the logging stream handler to allow for tqdm progress bars."""

    def __init__(self, stream):
        super().__init__(stream)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            self.handleError(record)


class CATMiner:
    def __init__(self, in_dir: str, out_dir: str, file_type: int = 0, **kwargs):
        """The CATMiner class is used to extract data in a batch process.

        Parameters
        ----------
        in_dir: str
            The input path.
        out_dir: str
            The output path.
        file_type: int
            The file types represented as an integer (e.g. catminer.XML, catminer.JSON)
        """
        self.browser = pyvba.Browser(kwargs.get('app', 'CATIA.Application'))

        # path variables
        self._in_dir = os.path.abspath(in_dir)
        self._out_dir = os.path.abspath(out_dir)
        self._tmp_dir = os.path.join(self._out_dir, '.catminer')
        self._file_type = file_type

        # timing and progress variables
        self._start_time = time.perf_counter()
        self._to_convert = len(cat_file_list(self._in_dir))
        self._file_num = 1
        self._pbar = None

        self._kwargs = kwargs

        # change logger properties
        global logger
        [logger.removeHandler(i) for i in logger.handlers]

        log_path = os.path.join(self._out_dir, 'logs')
        os.makedirs(log_path, exist_ok=True)
        log_name = f'catminer-{datetime.now().strftime("%d-%m-%Y")}.log'

        fh = logging.FileHandler(os.path.join(log_path, log_name), 'a')
        sh = TQDMStreamHandler(sys.stdout)

        fh.setLevel(logging.INFO)
        sh.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(sh)
        logger.setLevel(logging.INFO)

    def begin(self) -> None:
        """Commence the data-mining process once setting are in place, if applicable."""
        # start printing to the log
        text_art = textwrap.dedent(r"""            
                         _               _
              ___  __ _ | |_  _ __ ___  (_) _ __    ___  _ __
             / __|/ _` || __|| '_ ` _ \ | || '_ \  / _ \| '__|
            | (__| (_| || |_ | | | | | || || | | ||  __/| |
             \___|\__,_| \__||_| |_| |_||_||_| |_| \___||_|
            ==================================================""")
        print(text_art)
        logger.info('CATMINER RUNNING...')
        logger.info(f'Found {self._to_convert} .CAT* files to convert.')
        self._pbar = tqdm(total=self._to_convert, desc='Progress: ', unit="file")

        # begin the catminer process
        try:
            self._dir_crawl(self._in_dir, self._out_dir)
        except KeyboardInterrupt:
            logger.critical('User break detected, stopping catminer gracefully...')
        except BaseException:
            # log error
            exc_type, exc_value, exc_traceback = sys.exc_info()
            [
                logger.critical(re.sub(r'(\n| {2,})', '', str(i)))
                for i in traceback.format_exception(exc_type, exc_value, exc_traceback)
            ]
        finally:
            self._finish()

    def _dir_crawl(self, in_dir: str, out_dir: str) -> None:
        """Crawl through, process, and duplicate the directory.

        This function is tasked to iterating through the directory tree. If a CATIA file is encountered, an export
        process will be launched. If a zip file is encountered, it will be opened and the crawl will proceed. If a
        folder is encountered, it will be duplicated in the respective output folder.
        """
        for file in os.listdir(in_dir):
            file_path = os.path.join(in_dir, file)

            # skip if reading the output directory
            if file_path == self._out_dir:
                continue

            # directory found -> scan it
            if os.path.isdir(file_path) and cat_in_dir(file_path):
                dir_path = os.path.join(out_dir, file)

                if not os.path.exists(dir_path):
                    logger.info(f'Created path: {dir_path}.')
                    os.mkdir(dir_path)

                self._dir_crawl(file_path, dir_path)

            # file found
            elif os.path.isfile(file_path):
                # zipfile found -> unzip it and scan it
                if zf.is_zipfile(file_path):
                    with zf.ZipFile(file_path, 'r') as zfile:
                        file_name = file_re.findall(zfile.filename)[0]
                        new_out_dir = os.path.join(out_dir, file_name)
                        tmp_path = os.path.join(self._tmp_dir, new_out_dir.replace(self._out_dir, '')[1:])

                        # create missing directories
                        if not os.path.exists(new_out_dir):
                            logger.info(f'Created path: {new_out_dir}.')
                            os.mkdir(new_out_dir)
                        if not os.path.exists(tmp_path):
                            logger.info(f'Created path: {tmp_path}.')
                            os.makedirs(tmp_path, exist_ok=True)

                        # extract zip to temp location and continue
                        zfile.extractall(tmp_path)
                        self._dir_crawl(tmp_path, new_out_dir)

                # CATIA file found
                elif type_re.search(file_path):
                    # check if file has been previously processed
                    if not self._kwargs.get('force_export', False) and os.path.exists(out_dir):
                        extension_dict = {str(XML): '.xml', str(JSON): '.json'}
                        extension = extension_dict[str(self._file_type)]
                        file_loc = os.path.join(out_dir, file + extension)

                        if os.path.exists(file_loc):
                            logger.warning(f'Skipping "{file}" ({self._file_num}/{self._to_convert}). '
                                           f'File already exported!')
                            self._file_num += 1
                            self._pbar.update(1)
                            continue

                    self._export_file(os.path.join(in_dir, file), out_dir)

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
            file_type = type_re.findall(cat_file)[0]

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

    def _export_file(self, in_dir: str, out_dir: str) -> None:
        """Exports a CATIA file to a specified location using pyvba.

        Parameters
        ----------
        in_dir: str
            The path of the file.
        out_dir: str
            The output path for the exported file.

        Notes
        -----
        The document is opened in CATIA then closed when finished. Errors are logged.
        """
        file_name = file_re.findall(in_dir)[0]
        file_type = type_re.findall(in_dir)[0]
        full_name = file_name + '.CAT' + file_type

        # open the file
        logger.info(f"Opening \"{full_name}\" ({self._file_num}/{self._to_convert}).")
        opened_file = self.browser.Documents.Open(in_dir)

        try:
            browser = self._cat_type(in_dir)

            # select the right exporter
            if self._file_type == 1:
                exporter = pyvba.JSONExport(browser, skip_func=True, skip_err=True)
            else:
                exporter = pyvba.XMLExport(browser, skip_func=True, skip_err=True)

            # export the file and time it
            timer(
                f"export for \"{full_name}\" ({self._file_num}/{self._to_convert})"
            )(exporter.save)(full_name, out_dir)
            self._file_num += 1
            self._pbar.update(1)
        finally:
            # ensure that the file closes
            opened_file.Close()
            time.sleep(0.5)

    def _finish(self) -> None:
        """Cleans up any open files."""
        self.browser = None
        try:
            logger.info(f'Removing {self._tmp_dir}.')
            shutil.rmtree(self._tmp_dir)
        except FileNotFoundError:
            logger.error('Directory ".catminer" not found! Skipping removal...')

        # check total time
        total_time = time.perf_counter() - self._start_time
        self._pbar.close()
        logger.info(f"Finished batch export in {total_time:.4f} seconds.\n")


if __name__ == "__main__":
    if not os.path.exists(r"..\output"):
        os.mkdir(r"..\output")

    CATMiner(r"..\input", r"..\output").begin()
