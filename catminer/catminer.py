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


# define regular expressions
type_re = re.compile(r'(?<=\.CAT)[^.]*?$')
file_re = re.compile(r'[^\\]+(?=\.)')

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


class CATMiner:
    def __init__(self, path: str, out_dir: str, file_type: int = 0, **kwargs):
        """The CATMiner class is used to extract data in a batch process.

        Parameters
        ----------
        path: str
            The input path.
        out_dir: str
            The output path.
        file_type: int
            The file types represented as an integer (e.g. catminer.XML, catminer.JSON)
        """
        self.browser = pyvba.Browser(kwargs.get('app', 'CATIA.Application'))
        self._path = os.path.abspath(path)
        self._out_dir = os.path.abspath(out_dir)
        self._tmp_dir = os.path.join(self._out_dir, '.catminer')
        self._file_type = file_type
        self._start_time = time.perf_counter()
        self._kwargs = kwargs

        # change logger properties
        global logger
        [logger.removeHandler(i) for i in logger.handlers]

        fh = logging.FileHandler(os.path.join(self._out_dir, r'catminer.log'), 'w')
        sh = logging.StreamHandler(sys.stdout)

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
        text_art = textwrap.dedent(r"""
                         _               _
              ___  __ _ | |_  _ __ ___  (_) _ __    ___  _ __
             / __|/ _` || __|| '_ ` _ \ | || '_ \  / _ \| '__|
            | (__| (_| || |_ | | | | | || || | | ||  __/| |
             \___|\__,_| \__||_| |_| |_||_||_| |_| \___||_|
            ==================================================""")
        print(text_art)
        logger.info('CATMINER RUNNING...')

        try:
            self._dir_crawl(self._path, self._out_dir)
        except BaseException:
            # log error
            exc_type, exc_value, exc_traceback = sys.exc_info()
            [
                logger.critical(re.sub(r'(\n| {2,})', '', str(i)))
                for i in traceback.format_exception(exc_type, exc_value, exc_traceback)
            ]
        finally:
            self._finish()

    def _dir_crawl(self, path: str, out_dir: str) -> None:
        """Crawl through, process, and duplicate the directory.

        This function is tasked to iterating through the directory tree. If a CATIA file is encountered, an export
        process will be launched. If a zip file is encountered, it will be opened and the crawl will proceed. If a
        folder is encountered, it will be duplicated in the respective output folder.
        """
        for file in os.listdir(path):
            file_path = os.path.join(path, file)

            # skip if reading the output directory
            if file_path == self._out_dir:
                continue

            # directory found -> scan it
            if os.path.isdir(file_path):
                dir_path = os.path.join(out_dir, file)

                if not os.path.exists(dir_path):
                    logger.info(f'Created path: {dir_path}.')
                    os.mkdir(dir_path)

                self._dir_crawl(file_path, dir_path)

            # file found
            elif os.path.isfile(file_path):
                # zipfile found -> unzip it and scan it
                if zf.is_zipfile(file_path):
                    with zf.ZipFile(file_path) as zfile:
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
                        file_name = file_re.findall(file_path)[0]
                        file_type = type_re.findall(file_path)[0]
                        extension_dict = {str(XML): '.xml', str(JSON): '.json'}
                        extension = extension_dict[str(self._file_type)]
                        file_loc = os.path.join(out_dir, file_name + extension)

                        if os.path.exists(file_loc):
                            logger.warning(f'Skipping "{file_name + ".CAT" + file_type}". File already exported!')
                            continue

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
        file_name = file_re.findall(path)[0]
        file_type = type_re.findall(path)[0]

        # open the file
        logger.info(f"Opening \"{file_name + '.CAT' + file_type}\".")
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
        try:
            logger.info(f'Removing {self._tmp_dir}.')
            shutil.rmtree(self._tmp_dir)
        except FileNotFoundError:
            logger.error('Directory ".catminer" not found! Skipping removal...')

        # check total time
        total_time = time.perf_counter() - self._start_time
        logger.info(f"Finished batch export in {total_time:.4f} seconds.")


if __name__ == "__main__":
    if not os.path.exists(r"..\output"):
        os.mkdir(r"..\output")

    CATMiner(r"..\input", r"..\output").begin()
