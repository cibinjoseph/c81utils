"""Reading and writing C81 coefficient tables as CSV.

The CSV representation holds up to three tables (CL, CD, CM, in that order)
separated by one or more blank lines. Each table looks like::

    0,  0.0, 0.3, 0.6      <- placeholder, then Mach numbers
    -10, -0.8, -0.7, -0.6  <- angle of attack [deg], then coefficients
    0,   0.0,  0.0,  0.0
    10,  0.8,  0.7,  0.6

Cells may be separated by commas or by whitespace (decided per table). Text
after ``#`` is a comment. Grids are never sorted or resampled.
"""

import math
import os
from pathlib import Path
from typing import IO, List, Optional, Tuple, Union

import numpy as np

from .core import C81

PathOrFile = Union[str, 'os.PathLike[str]', IO[str]]

_LABELS = ('CL', 'CD', 'CM')

# A parsed table: (Mach grid, alpha grid, coefficient matrix)
_Table = Tuple[np.ndarray, np.ndarray, np.ndarray]


def _is_path(obj) -> bool:
    return isinstance(obj, (str, os.PathLike))


def _split_tables(text: str) -> List[List[Tuple[int, str]]]:
    """Split text into tables of (line number, content) pairs.

    Blank (whitespace-only) lines separate tables, however many there are.
    Comment-only lines are dropped without separating tables.
    """
    tables = []  # type: List[List[Tuple[int, str]]]
    current = []  # type: List[Tuple[int, str]]
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            if current:
                tables.append(current)
                current = []
            continue
        content = raw.split('#', 1)[0].strip()
        if content:
            current.append((lineno, content))
    if current:
        tables.append(current)
    return tables


def _parse_table(rows: List[Tuple[int, str]], label: str) -> _Table:
    """Convert the lines of one table into (mach, alpha, values) arrays."""
    use_comma = any(',' in content for _, content in rows)

    data = []
    for lineno, content in rows:
        if use_comma:
            cells = [c.strip() for c in content.split(',')]
        else:
            cells = content.split()
        row = []
        for cell in cells:
            if not cell or '_' in cell:
                raise ValueError(
                    '{} table, line {}: invalid value {!r}{}'.format(
                        label, lineno, cell,
                        ' (mixed delimiters or empty cell?)' if use_comma else ''))
            try:
                number = float(cell)
            except ValueError:
                raise ValueError(
                    '{} table, line {}: cannot convert {!r} to a number{}'.format(
                        label, lineno, cell,
                        ' (mixed delimiters?)' if use_comma else '')) from None
            if not math.isfinite(number):
                raise ValueError(
                    '{} table, line {}: non-finite value {!r} is not allowed'
                    .format(label, lineno, cell))
            row.append(number)
        data.append((lineno, row))

    ncols = len(data[0][1])
    for lineno, row in data:
        if len(row) != ncols:
            raise ValueError(
                '{} table, line {}: expected {} values per row (as in the '
                'first row) but found {}'.format(label, lineno, ncols, len(row)))
    if len(data) < 3 or ncols < 3:
        raise ValueError(
            '{} table must contain a header row plus at least two angle rows '
            'and two Mach columns (found {} rows by {} columns)'.format(
                label, len(data), ncols))

    arr = np.array([row for _, row in data], dtype=float)
    mach = arr[0, 1:].copy()
    alpha = arr[1:, 0].copy()
    values = arr[1:, 1:].copy()

    if not np.all(np.diff(mach) > 0):
        raise ValueError('{} table: Mach numbers must be strictly increasing'
                         .format(label))
    if not np.all(np.diff(alpha) > 0):
        raise ValueError('{} table: angles of attack must be strictly '
                         'increasing'.format(label))
    return mach, alpha, values


def _default_name(source) -> str:
    if _is_path(source):
        return Path(source).stem
    name = getattr(source, 'name', None)
    if isinstance(name, str) and name:
        return Path(name).stem
    return 'unnamed'


def load_csv(source: PathOrFile, name: Optional[str] = None) -> C81:
    """Read a CSV file with CL, CD and CM tables into a :class:`C81` object.

    Parameters
    ----------
    source
        Path (``str`` or ``pathlib.Path``) or text file-like object.
    name
        Airfoil name. Defaults to the file stem, or ``'unnamed'`` if the
        source has no file name.

    Notes
    -----
    One table is taken as CL, two as CL and CD, three as CL, CD and CM. A
    missing CD or CM table is filled with zeros on the CL angle-of-attack and
    Mach grids. The tables may use different grids.

    Raises
    ------
    ValueError
        If the data is empty, has more than three tables, is malformed,
        contains NaN/infinity, or has grids that are not strictly increasing.
    FileNotFoundError
        If ``source`` is a path that does not exist.
    """
    if name is not None and not isinstance(name, str):
        raise TypeError('name must be a str')
    if name is None:
        name = _default_name(source)

    if _is_path(source):
        with open(source, 'r', encoding='utf-8-sig') as fh:
            text = fh.read()
    else:
        text = source.read()
        if isinstance(text, bytes):
            text = text.decode('utf-8-sig')
        text = text.lstrip('\ufeff')

    raw_tables = _split_tables(text)
    if not raw_tables:
        raise ValueError('no data found: the CSV input is empty')
    if len(raw_tables) > 3:
        raise ValueError(
            'found {} tables but at most 3 (CL, CD, CM) are allowed; tables '
            'must be separated by blank lines'.format(len(raw_tables)))

    tables = [_parse_table(rows, _LABELS[i])
              for i, rows in enumerate(raw_tables)]
    mach_l, alpha_l, cl = tables[0]
    # Absent CD/CM tables default to zeros on the CL grids
    zeros = (mach_l.copy(), alpha_l.copy(), np.zeros_like(cl))
    mach_d, alpha_d, cd = tables[1] if len(tables) > 1 else zeros
    mach_m, alpha_m, cm = tables[2] if len(tables) > 2 else zeros

    return C81(name,
               alpha_l, mach_l, cl,
               alpha_d, mach_d, cd,
               alpha_m, mach_m, cm)


def _format_table(alpha: np.ndarray, mach: np.ndarray, values: np.ndarray) -> str:
    """Format one table; repr() gives the shortest string that round-trips."""
    def fmt(x) -> str:
        return repr(float(x))

    lines = [','.join(['0'] + [fmt(m) for m in mach])]
    for a, row in zip(alpha, values):
        lines.append(','.join([fmt(a)] + [fmt(v) for v in row]))
    return '\n'.join(lines) + '\n'


def dump_csv(c81Data: C81, dest: PathOrFile) -> None:
    """Write the CL, CD and CM tables of ``c81Data`` as CSV.

    The three tables are written one after another, separated by a blank
    line. Each table is written with its own grids, so they may differ in
    size. Values are written at full floating-point precision.

    Parameters
    ----------
    c81Data
        The airfoil data.
    dest
        Path (``str`` or ``pathlib.Path``) or text file-like object.
    """
    text = '\n'.join(_format_table(t.alpha, t.mach, t.val)
                     for t in (c81Data.CL, c81Data.CD, c81Data.CM))
    if _is_path(dest):
        with open(dest, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
    else:
        dest.write(text)
