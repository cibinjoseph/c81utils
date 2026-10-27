"""Command-line interface: ``c81-convert``."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .convert import c81_to_csv, csv_to_c81, load_c81
from .csv_io import load_csv
from .plotting import MATPLOTLIB_HINT, plot

PROG = 'c81-convert'


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description='Convert between CSV and C81 airfoil table files. The '
                    'direction is chosen from the input file extension '
                    '(.csv -> .c81, .c81 -> .csv, case-insensitive).',
        epilog='Exit status: 0 on success, 1 if any file failed, '
               '2 on invalid usage.')
    parser.add_argument('inputs', nargs='+', metavar='FILE',
                        help='input .csv or .c81 file(s)')
    parser.add_argument('-o', '--output', metavar='PATH',
                        help='output path (only valid with a single input)')
    parser.add_argument('--plot', action='store_true',
                        help='plot CL, CD and CM instead of converting '
                             '(needs Matplotlib)')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    return parser


def _error(message: str) -> None:
    print('{}: error: {}'.format(PROG, message), file=sys.stderr)


def _plot_files(paths: List[Path]) -> int:
    status = 0
    plotted = False
    for path in paths:
        try:
            airfoil = load_csv(path) if path.suffix.lower() == '.csv' else load_c81(path)
            plot(airfoil)
            plotted = True
        except ImportError:
            _error(MATPLOTLIB_HINT)
            return 1
        except (OSError, ValueError) as err:
            _error(str(err))
            status = 1
    if plotted:
        import matplotlib.pyplot as plt
        plt.show()
    return status


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point of ``c81-convert``. Returns the process exit status."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.output is not None and (len(args.inputs) > 1 or args.plot):
        parser.error('-o/--output can only be used with a single input file '
                     'and cannot be combined with --plot')

    paths = [Path(p) for p in args.inputs]
    bad = [p for p in paths if p.suffix.lower() not in ('.csv', '.c81')]
    if bad:
        for p in bad:
            _error("unsupported file extension '{}' for {} (expected .csv or "
                   ".c81)".format(p.suffix, p))
        return 2

    if args.plot:
        return _plot_files(paths)

    status = 0
    for path in paths:
        try:
            if path.suffix.lower() == '.csv':
                out = csv_to_c81(path, args.output)
            else:
                out = c81_to_csv(path, args.output)
        except (OSError, ValueError) as err:
            _error(str(err))
            status = 1
        else:
            print(out)
    return status


if __name__ == '__main__':
    sys.exit(main())
