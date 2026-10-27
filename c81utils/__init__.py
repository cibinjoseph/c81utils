"""c81utils: tools for working with C81 airfoil coefficient tables."""

# Kept free of heavy imports above this line so that packaging tools can read
# the version statically.
__version__ = '1.1.0'

from .core import C81, CoeffTable, dump, load
from .csv_io import dump_csv, load_csv
from .convert import c81_to_csv, csv_to_c81
from .plotting import plot

__all__ = [
    'C81', 'CoeffTable', 'load', 'dump',
    'load_csv', 'dump_csv', 'csv_to_c81', 'c81_to_csv', 'plot',
    '__version__',
]
