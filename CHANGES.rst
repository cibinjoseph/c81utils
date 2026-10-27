1.1.0 (2026-10-27)
--------------------
* Merge the functionality of `csv-c81 <https://github.com/cibinjoseph/csv-c81>`_ into c81utils.
* Add ``load_csv()`` and ``dump_csv()`` for reading/writing CSV (paths or file objects).
  Up to three tables (CL, CD, CM) separated by blank lines; comma or whitespace delimited
  (decided per table); ``#`` comments. Missing CD/CM tables are set to zero on the CL grids.
  CL, CD and CM may have different grids. Input is validated (shape, NaN/inf, malformed
  numbers, strictly increasing grids, at most three tables) and never sorted or resampled.
* Add ``csv_to_c81()`` and ``c81_to_csv()`` for path-based conversion. Extensions are matched
  case-insensitively, the default output name is the input name with the new extension, and
  an input file is never overwritten.
* Add the ``c81-convert`` command (also ``python -m c81utils``) with ``--plot``.
* Add ``plot()`` (Matplotlib is optional: ``pip install "c81utils[plot]"``).
* The module is now a package (``c81utils/``); ``import c81utils`` and the existing API
  (``C81``, ``CoeffTable``, ``load``, ``dump``) are unchanged.
* Packaging moved from ``setup.py`` to ``pyproject.toml``; Python 3.9 or newer is required.
* Tests moved to pytest (existing unittest tests still run) and no longer depend on the
  working directory.
* Improvements over csv-c81: CSV export works when CL/CD/CM sizes differ and keeps full
  precision; delimiters are detected per table; extra tables are rejected instead of being
  silently used as CM; user errors no longer print tracebacks.
* Known limitations (unchanged): C81 files hold 3 decimals; ``dump()`` writes table sizes
  with two digits, so tables with more than 99 values per axis are not supported;
  ``C81.__eq__`` only compares CL.

1.0.7 (2022-09-07)
--------------------
* Fix multiline data recognition.

1.0.5 (2021-07-21)
--------------------
* Ensure mach and alpha arrays have atleast two values.

1.0.4 (2021-07-21)
--------------------
* Ensure mach and alpha arrays are strictly increasing.

1.0.0 (2020-04-25)
--------------------
* Initial release.
