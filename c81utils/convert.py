"""Path-based conversion between CSV and C81 files."""

import io
import os
from pathlib import Path
from typing import Optional, Union

from .core import C81, dump, load
from .csv_io import dump_csv, load_csv

PathLike = Union[str, 'os.PathLike[str]']


def _check_input(path: PathLike, expected_ext: str) -> Path:
    path = Path(path)
    if path.suffix.lower() != expected_ext:
        raise ValueError('{}: expected a {} file (extension is case-insensitive)'
                         .format(path, expected_ext))
    if not path.is_file():
        raise FileNotFoundError('{}: no such file'.format(path))
    return path


def _resolve_output(input_path: Path, output: Optional[PathLike],
                    new_ext: str) -> Path:
    out = input_path.with_suffix(new_ext) if output is None else Path(output)
    same = out.resolve() == input_path.resolve()
    if not same and out.exists():
        same = os.path.samefile(out, input_path)
    if same:
        raise ValueError('output path {} is the same file as the input; '
                         'refusing to overwrite it'.format(out))
    return out


def csv_to_c81(input: PathLike, output: Optional[PathLike] = None,
               name: Optional[str] = None) -> Path:
    """Convert a CSV file to a C81 file and return the output path.

    Parameters
    ----------
    input
        Path to a ``.csv`` file (extension is case-insensitive).
    output
        Output path. Defaults to the input path with a ``.c81`` extension.
    name
        Airfoil name stored in the C81 header. Defaults to the CSV file stem.
    """
    in_path = _check_input(input, '.csv')
    out_path = _resolve_output(in_path, output, '.c81')
    airfoil = load_csv(in_path, name=in_path.stem if name is None else name)
    buffer = io.StringIO()
    dump(airfoil, buffer)
    # Write only once everything succeeded so failures leave no partial file
    with open(out_path, 'w') as fh:
        fh.write(buffer.getvalue())
    return out_path


def load_c81(path: PathLike) -> C81:
    """Read a C81 file by path, with a descriptive error if it is invalid."""
    try:
        with open(path, 'r') as fh:
            return load(fh)
    except (ValueError, IndexError) as err:
        raise ValueError('{}: not a valid C81 file ({})'.format(path, err)) from err


def c81_to_csv(input: PathLike, output: Optional[PathLike] = None) -> Path:
    """Convert a C81 file to a CSV file and return the output path.

    Parameters
    ----------
    input
        Path to a ``.c81`` file (extension is case-insensitive).
    output
        Output path. Defaults to the input path with a ``.csv`` extension.
    """
    in_path = _check_input(input, '.c81')
    out_path = _resolve_output(in_path, output, '.csv')
    airfoil = load_c81(in_path)
    dump_csv(airfoil, out_path)
    return out_path
