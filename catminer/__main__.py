import argparse
import os
import sys

import catminer


def check_dir(path: str) -> bool:
    """Check if directory or folder exists.

    Parameters
    ----------
    path: str
        Path to directory or file.

    Returns
    -------
    bool
        Returns true if the directory exists.
    """
    path = os.path.abspath(path)

    if os.path.exists(path) and not os.path.isdir(path):
        raise NotADirectoryError(f"Directory of {path} not found.")

    if not os.path.exists(path):
        response = input(f"{path} was not found.\n"
                         "Would you like to create the directory [Y] or abort [N]?\n"
                         "Enter Y/N: ")
        if response == 'y' or response == 'Y':
            os.makedirs(path)
            return True
        else:
            print("Exiting...")
            sys.exit(0)

    return os.path.exists(path)


def main():
    # create parser and subparsers
    parser = argparse.ArgumentParser(description='These are the available commands for catminer:',
                                     epilog='Use "catminer <command> -h" to get more help on the command.')
    subparsers = parser.add_subparsers(help='sub-commands', dest='command')

    # 'run' command
    run_parser = subparsers.add_parser('run', description='Run catminer using these commands:',
                                       help='run the batch process')

    run_parser.add_argument('-b', '--bat-file', nargs='?', const=os.getcwd(), default=os.getcwd(), type=str, metavar='path',
                            help='generate a .bat file for easier automation')
    run_parser.add_argument('-i', '--in_dir', nargs=1, default=os.getcwd(), type=str, metavar='path',
                            help='set the run directory')
    run_parser.add_argument('-o', '--out-dir', nargs=1, type=str, metavar='path', help='set the output directory')
    run_parser.add_argument('-f', '--force-export', action='store_true', help='export previously exported files')
    run_parser.add_argument('-t', '--file-type', nargs=1, default='xml', type=str, choices=['xml', 'json'],
                            help='choose the output file type (default: xml)')
    run_parser.add_argument('-r', '--relative-path', action='store_true', help='use the relative path to run catminer')

    # parse args
    args = None

    if 'pytest' in sys.argv[0]:
        args = parser.parse_args([])
    else:
        args = parser.parse_args()

    d_args = vars(args)

    # bring up 'run' help if no command input
    if 'run' not in sys.argv:
        parser.parse_args(args=['run', '-h'])

    # process arguments
    if args.command == 'run':
        # check for list instances
        for key, value in d_args.items():
            if isinstance(value, list):
                d_args[key] = d_args[key][0]

        # resolve out directory
        if args.out_dir is None:
            args.out_dir = os.path.join(os.getcwd(), 'catminer-output')
            os.makedirs(args.out_dir, exist_ok=True)

        # check the entered directories
        for i in ['in_dir', 'out_dir', 'bat_file']:
            if d_args['out_dir'] == os.path.join(os.getcwd(), 'catminer-output'):
                continue

            check_dir(d_args[i])

        # create bat file or start miner
        if '-b' in sys.argv:
            bat_str = f'python catminer run {"-f " if d_args.get("force_export", False) else ""}-t {args.file_type}^\n' + \
                f' -i "{"." if "-r" in sys.argv else args.in_dir}"^\n' + \
                f' -o "{os.path.join(".", "catminer") if "-r" in sys.argv else args.out_dir}"\n'

            with open(os.path.join(args.bat_file, "catminer.bat"), 'w') as f:
                f.write(bat_str)
                f.close()
        else:
            file_type = {'xml': catminer.XML, 'json': catminer.JSON}
            miner = catminer.CATMiner(args.in_dir, args.out_dir, file_type[args.file_type],
                                      force_export=d_args.get("force_export", False))
            miner.begin()


if __name__ == '__main__':
    main()