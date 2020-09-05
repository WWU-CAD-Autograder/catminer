# catminer
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/catminer)
[![PyPI](https://img.shields.io/pypi/v/catminer)](https://pypi.org/project/catminer/)
[![GitHub](https://img.shields.io/github/license/WWU-CAD-Autograder/catminer)](https://github.com/WWU-CAD-Autograder/catminer)

The catminer package is designed to data-mine from CATIA (.CAT*) files into readable formats. CATIA is a CAD design 
application developed by Dassault Systèmes.

## Getting Started
Install the Python package:
```
pip install catminer
```

To export data, navigate to the file or directory:
```
cd /d path
```
Open CATIA then run catminer:
```
catminer run
```
> Note 1: CATIA may not need to be open, however, the wrong version may launch.

> Note 2: Press `ctrl + c` momentarily to end the program gracefully. Alternatively, press `ctrl + break` for a 
> non-graceful exit.

<br>

For help on the export options:
```
catminer run -h
```
which yields the following:
```
usage: catminer run [-h] [-u USER_SETTINGS] [-i path] [-o path]
                    [-t {xml,json}] [-f] [--no-skips] [--active-doc]

Run catminer using these commands:

optional arguments:
  -h, --help            show this help message and exit
  -u USER_SETTINGS, --user-settings USER_SETTINGS
                        run using user-defined settings from the settings.ini
                        file
  -i path, --in-dir path
                        set the run directory
  -o path, --out-dir path
                        set the output directory
  -t {xml,json}, --file-type {xml,json}
                        choose the output file type (default: xml)
  -f, --force-export    overwrite previously exported files
  --no-skips            ignore the optimized skips - the process will take
                        much longer
  --active-doc          export the entire ActiveDocument instead of the part,
                        product, etc.
```

The supported outputs are dependent on [pyvba](https://pypi.org/project/pyvba/).

### Customization
The settings above can be customized to run by default or from custom setting groups. To customize these settings:
```
catminer edit
```

## Developer Notes
Contributors are welcome! The project is [hosted on GitHub](https://github.com/WWU-CAD-Autograder/catminer). Report 
any issues at [the issue tracker](https://github.com/WWU-CAD-Autograder/catminer/issues), but please check to see if 
the issue already exists!
