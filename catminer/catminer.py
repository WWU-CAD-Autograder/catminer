import argparse
import logging
import os
import pyvba
import re
import time
import zipfile

FILE_RE = re.compile(r'(?<=\.CAT)[^.]*?$')

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


class CATMiner:
    def __init__(self, path: str = None, out_dir: str = None):
        self.browser = pyvba.Browser('CATIA.Application')
        self._path = path if path is not None else r"..\input"
        self._out_dir = out_dir if out_dir is not None else r"..\output"

    def begin(self) -> None:
        """Commence the data-mining process once setting are in place, if applicable."""
        ...

    def _update_log(self) -> None:
        """Add an entry to the log and print out step."""
        ...

    def _dir_crawl(self) -> None:
        """Crawl through, process, and duplicate the directory.

        This function is tasked to iterating through the directory tree. If a CATIA file is encountered, an export
        process will be launched. If a zip file is encountered, it will be opened and the crawl will proceed. If a
        folder is encountered, it will be duplicated in the respective output folder.
        """
        ...

    def _create_folder(self, name: str, path: str) -> None:
        """Creates a named folder at a specified path.

        Parameters
        ----------
        name: str
            The name of the folder.
        path: str
            The path to the folder.
        """
        ...

    def _open_zip(self, path: str) -> list:
        """Opens a zip file and returns its contents.

        Parameters
        ----------
        path: str
            The location of the zip file.

        Returns
        -------
        list
            A list containing each unzipped file.
        """
        ...

    def _cat_type(self, cat_file_name: str) -> pyvba.Browser:
        """Return the browser object that correlates to the CATIA file being processed.

        Parameters
        ----------
        cat_file_name: str
            The CATIA.ActiveDocument.Name (i.e. the name of the file).

        Returns
        -------
        pyvba.Browser
            The VBA object that represents the correlated file type.
        """
        file_type = FILE_RE.findall(cat_file_name)[0]

        if file_type == "Product":
            return self.browser.ActiveDocument.Product
        elif file_type == "Part":
            return self.browser.ActiveDocument.Part
        elif file_type == "Drawing":
            return self.browser.ActiveDocument.DrawingRoot
        elif file_type == "Process":
            return self.browser.ActiveDocument.PPRDocument

        return self.browser

    def _export_file(self, path: str) -> None:
        """Exports a CATIA file to a specified location using pyvba.

        Parameters
        ----------
        path: str
            The output path for the exported file.

        Notes
        -----
        The document is opened in CATIA then closed when finished. Errors are logged.
        """
        ...

    def _finish(self) -> None:
        """Cleans up any open files."""
        ...


if __name__ == "__main__":
    ...
