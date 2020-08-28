# catminer
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/catminer)
[![PyPI](https://img.shields.io/pypi/v/catminer)](https://pypi.org/project/catminer/)
[![GitHub](https://img.shields.io/github/license/WWU-CAD-Autograder/catminer)](https://github.com/WWU-CAD-Autograder/catminer)

The catminer package is designed to data-mine from CATIA (.CAT*) files into readable formats. CATIA is a CAD design 
application developed by Dassault Systèmes.

## Getting Started
Install the Python package:
```cmd
pip install catminer
```

To export data, navigate to the file or directory:
```cmd
cd /d path
```
Open CATIA then run catminer:
```cmd
catminer run
```
> Note 1: CATIA may not need to be open, however, the wrong version may launch

> Note 2: Press `ctrl + c` for a second to end the program mid process. Alternatively, press `ctrl + break` for a 
> non-graceful exit.

<br>

For help on the export options:
```cmd
catminer run -h
```
which yields the following:
```
usage: catminer run [-h] [-i path] [-o path] [-f] [-t {xml,json}] [-b [path]]
                    [-r]

Run catminer using these commands:

optional arguments:
  -h, --help            show this help message and exit
  -i path, --in-dir path
                        set the run directory
  -o path, --out-dir path
                        set the output directory
  -f, --force-export    export previously exported files
  -t {xml,json}, --file-type {xml,json}
                        choose the output file type (default: xml)

.bat file:
  extra commands to make a .bat file instead

  -b [path], --bat-file [path]
                        generate a .bat file for easier automation
  -r, --relative-path   use the relative path to create the .bat file
```

The supported outputs are dependent on [pyvba](https://pypi.org/project/pyvba/).

## Developer Notes
Contributors are welcome! The project is [hosted on GitHub](https://github.com/WWU-CAD-Autograder/catminer). Report 
any issues at [the issue tracker](https://github.com/WWU-CAD-Autograder/catminer/issues), but please check to see if 
the issue already exists!
