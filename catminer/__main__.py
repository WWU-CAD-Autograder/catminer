import argparse
import configparser
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
            print("Starting catminer...")
            return True
        else:
            print("Exiting...")
            sys.exit(0)

    return os.path.exists(path)


def main():
    # create parser and subparsers
    parser = argparse.ArgumentParser(description='These are the available commands for catminer:',
                                     epilog='Use "catminer run -h" to get more help on the run command.')
    subparsers = parser.add_subparsers(help='sub-commands', dest='command')

    # version check
    parser.add_argument('-V', '--version', action='store_true', help='check which version of catminer is installed')

    # edit command
    subparsers.add_parser('edit', description='Modify the default settings using the following commands:',
                          help='edit catminer\'s settings file')

    # 'run' command
    run_parser = subparsers.add_parser('run', description='Run catminer using these commands:',
                                       help='run the batch export process')

    run_parser.add_argument('-u', '--user-settings', nargs=1, type=int, default=0,
                            help='run using user-defined settings from the settings.ini file')
    run_parser.add_argument('-i', '--in-dir', nargs=1, type=str, metavar='path', help='set the run directory')
    run_parser.add_argument('-o', '--out-dir', nargs=1, type=str, metavar='path', help='set the output directory')
    run_parser.add_argument('-t', '--file-type', nargs=1, type=str, choices=['xml', 'json'],
                            help='choose the output file type (default: xml)')
    run_parser.add_argument('-f', '--force-export', action='store_true', default=None,
                            help='overwrite previously exported files')
    run_parser.add_argument('--no-skips', action='store_true', default=None,
                            help='ignore the optimized skips - the process will take much longer')
    run_parser.add_argument('--active-doc', action='store_true', default=None,
                            help='export the entire ActiveDocument instead of the part, product, etc.')

    # parse args
    if 'pytest' in sys.argv[0]:
        args = parser.parse_args([])
    else:
        args = parser.parse_args()

    d_args = vars(args)

    # bring up help if no command input
    if not sys.argv[1:]:
        parser.parse_args(args=['-h'])

    # print version if requested
    if args.version:
        print('catminer version 1.3')
        sys.exit(1)

    # read in config file
    ini_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'settings.ini')
    config = configparser.ConfigParser()
    config.read(ini_file)

    # process arguments
    if args.command == 'run':
        # check for list instances
        for key, value in d_args.items():
            if isinstance(value, list):
                d_args[key] = d_args[key][0]

        # read config settings
        if args.user_settings > 0:
            try:
                settings = config[f'UserSettings.{args.user_settings}']
            except KeyError:
                print(f'UserSettings.{args.user_settings} was not found!\n'
                      f'Exiting...')
                sys.exit(-1)
        else:
            settings = config['DEFAULT']

        # settle conflict hierarchy
        d_args['in_dir'] = settings['InputDirectory'] if d_args['in_dir'] is None else d_args['in_dir']
        d_args['in_dir'] = os.getcwd() if d_args['in_dir'] == 'None' else d_args['in_dir']
        check_dir(d_args['in_dir'])

        d_args['out_dir'] = settings['OutputDirectory'] if d_args['out_dir'] is None else d_args['out_dir']
        d_args['out_dir'] = os.path.join(os.getcwd(), 'catminer-output') \
            if d_args['out_dir'] == 'None' else d_args['out_dir']
        if args.out_dir == os.path.join(os.getcwd(), 'catminer-output'):
            os.makedirs(args.out_dir, exist_ok=True)
        else:
            check_dir(d_args['out_dir'])

        d_args['file_type'] = settings['FileType'] if d_args['file_type'] is None else d_args['file_type']
        d_args['skip_ext'] = settings['SkipExtensions'].split(', ') if settings['SkipExtensions'] != 'None' else []
        d_args['skip_list'] = settings['SkipKeywords'].split(', ') if settings['SkipKeywords'] != 'None' else []
        d_args['force_export'] = settings.getboolean('ForceExport') \
            if d_args['force_export'] is None else d_args['force_export']
        d_args['no_skips'] = settings.getboolean('NoSkips') if d_args['no_skips'] is None else d_args['no_skips']
        d_args['active_doc'] = settings.getboolean('ActiveDocument') \
            if d_args['active_doc'] is None else d_args['active_doc']

        # start catminer
        file_type = {'xml': catminer.XML, 'json': catminer.JSON}
        miner = catminer.CATMiner(
            d_args['in_dir'], d_args['out_dir'], file_type[d_args['file_type']],
            skip_ext=d_args['skip_ext'],
            skip_list=d_args['skip_list'],
            force_export=d_args['force_export'],
            no_skips=d_args['no_skips'],
            active_doc=d_args['active_doc']
        )
        miner.begin()
    elif args.command == 'edit':
        os.startfile(ini_file)


if __name__ == '__main__':
    main()
