import argparse
import os
import catminer

# create parser and subparsers
parser = argparse.ArgumentParser(description='These are the available commands for catminer:',
                                 epilog='Use "catminer <command> -h" to get more help on the command.')
subparsers = parser.add_subparsers(help='sub-commands')

# 'run' command
run_parser = subparsers.add_parser('run', description='Run catminer using these commands:',
                                   help='run the batch process')

run_parser.add_argument('-b', '--bat-file', nargs=1, default=os.getcwd(), type=str, metavar='path',
                        help='generate a .bat file for easier automation')
run_parser.add_argument('-d', '--dir', nargs=1, default=os.getcwd(), type=str, metavar='path',
                        help='the run directory')
run_parser.add_argument('-f', '--file-type', nargs=1, default='xml', type=str, choices=['xml', 'json'],
                        help='choose the output file type (default: xml)')
run_parser.add_argument('-o', '--out-dir', nargs=1, type=str, metavar='path', help='set the output directory')
run_parser.add_argument('-r', '--relative-path', action='store_true', help='use the relative path to run catminer')

# parse args
args = parser.parse_args()

# bring up 'run' help if no command input
if len(vars(args)) == 0:
    parser.parse_args(args=['run', '-h'])

print(args)

