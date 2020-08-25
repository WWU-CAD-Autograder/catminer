# catminer
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/catminer)
[![PyPI](https://img.shields.io/pypi/v/catminer)](https://pypi.org/project/catminer/)
[![GitHub](https://img.shields.io/github/license/WWU-CAD-Autograder/catminer)](https://github.com/WWU-CAD-Autograder/catminer)

The catminer package is designed to data-mine from CATIA (.CAT*) files into readable formats. CATIA is a CAD software 
developed by Dassault Systèmes.

## Getting Started
Install the Python package:
```cmd
pip install catminer
```

To export data, navigate to the file or directory:
```cmd
cd <file or directory>
```
Then, run catminer:
```cmd
catminer run
```

<br>

For help on the export options:
```cmd
catminer run -h
```
which yields the following:
```
usage: catminer run [-h] [-b [path]] [-i path] [-o path] [-f] [-t {xml,json}]
                    [-r]

Run catminer using these commands:

optional arguments:
  -h, --help            show this help message and exit
  -b [path], --bat-file [path]
                        generate a .bat file for easier automation
  -i path, --in_dir path
                        the run directory
  -o path, --out-dir path
                        set the output directory
  -f, --force-export    export previously exported files
  -t {xml,json}, --file-type {xml,json}
                        choose the output file type (default: xml)
  -r, --relative-path   use the relative path to run catminer
```

The current supported output are dependent on [pyvba](https://pypi.org/project/pyvba/).

## Developer Notes
Contributors are welcome! The project is [hosted on GitHub](https://github.com/WWU-CAD-Autograder/catminer). Report 
any issues at [the issue tracker](https://github.com/WWU-CAD-Autograder/catminer/issues), but please check to see if 
the issue already exists!
