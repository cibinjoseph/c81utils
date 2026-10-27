.. image:: https://img.shields.io/pypi/v/c81utils.svg
   :target: https://pypi.org/project/c81utils/
   :alt: c81utils on PyPI

.. image:: https://travis-ci.com/cibinjoseph/c81utils.svg?token=FMmn3XQeRECGNsy6mT6B&branch=master
   :target: https://travis-ci.com/cibinjoseph/c81utils

c81utils
=========
Read, write, interpolate, convert and plot C81 airfoil tables.
Includes a ``c81-convert`` command for converting between C81 and CSV.

Installation
-------------

.. code-block:: bash

    pip install c81utils            # core
    pip install "c81utils[plot]"    # + Matplotlib, for plotting

Quick start
------------

.. code-block:: python

    import c81utils as c81

    # CSV -> C81 file (writes NACA0012.c81 next to the CSV)
    c81.csv_to_c81("NACA0012.csv")

    # Load the C81 file and interpolate (bilinear in alpha [deg] and Mach)
    with open("NACA0012.c81") as f:
        airfoil = c81.load(f)

    cl = airfoil.getCL(5.0, 0.3)
    cd = airfoil.getCD(5.0, 0.3)
    cm = airfoil.getCM(5.0, 0.3)

    # No C81 file needed: load the CSV directly
    airfoil = c81.load_csv("NACA0012.csv")
    cl = airfoil.getCL(5.0, 0.3)

    # C81 -> CSV, to inspect or edit the tables in a spreadsheet
    c81.c81_to_csv("NACA0012.c81")

    # Write a loaded airfoil as CSV; paths or open text files both work
    c81.dump_csv(airfoil, "edited.csv")

    # Plot (needs c81utils[plot]); returns (fig, axes), does not call show()
    fig, axes = c81.plot(airfoil)
    fig.savefig("NACA0012.png")

Command line
-------------

.. code-block:: bash

    c81-convert airfoil.csv                 # -> airfoil.c81
    c81-convert airfoil.c81                 # -> airfoil.csv
    c81-convert airfoil.csv -o result.c81   # explicit output (single input only)
    c81-convert a.csv b.csv c.c81           # several files at once
    c81-convert --plot airfoil.c81          # plot CL, CD, CM vs alpha

The direction is chosen from the extension (case-insensitive). Output files
are printed; errors go to stderr with exit status 1 (2 for bad usage).
An input file is never overwritten.

CSV format
-----------

.. code-block:: text

    # CL: first row = Mach numbers (first cell is a placeholder)
    0,   0.0,  0.3,  0.6
    -10, -0.8, -0.7, -0.6
    0,   0.0,  0.0,  0.0
    10,  0.8,  0.7,  0.6

    # CD (optional), after a blank line
    0,   0.0,  0.6
    -10, 0.02, 0.03
    10,  0.02, 0.03

* Up to three tables, in the order CL, CD, CM, separated by blank lines.
* First column is alpha in degrees; commas or whitespace; ``#`` starts a comment.
* A missing CD or CM table becomes zeros on the CL alpha and Mach grids.
* Each table may have its own grids (different sizes are fine).
* Grids must be strictly increasing (they are never sorted or resampled).
  NaN/inf, ragged rows, non-numeric text and more than three tables are errors.

Note: C81 files store coefficients with 3 decimals, so a CSV -> C81 -> CSV
round trip rounds the data. CSV files keep full precision.

C81 class
----------
*c81utils* implements a ``C81`` class that handles the C81 data for each airfoil.
A few example usages are shown below:

.. code-block:: python

    import c81utils
    import numpy as np    # Works with numpy arrays too

    # Use 'load' to obtain data from a C81 formatted text file
    with open("NACA0012.C81", "r") as f:
      naca0012 = c81utils.load(f)

    # Use the 'get' commands to obtain bilinearly interpolated data
    desiredAlpha = 5.0    # in degrees
    desiredMach = 0.3
    desiredCL = naca0012.getCL(desiredAlpha, desiredMach)
    desiredCD = naca0012.getCD(desiredAlpha, desiredMach)
    desiredCM = naca0012.getCM(desiredAlpha, desiredMach)

    # Combine 'get' commands with the 'map' command to operate on lists
    desiredAlpha = np.linspace(0, 10, 6)
    desiredMach = [0.0, 0.1, 0.0, 0.3, 0.5, 0.8]
    desiredCL = list(map(naca0012.getCL, desiredAlpha, desiredMach))

    # Data may also be input using arrays
    alpha = [0, 2, 4, 6]
    mach = [0.0, 0.5, 1.0]
    Cx = [[0.0, 0.0, 0.0],
          [0.2, 0.2, 0.2],
          [0.4, 0.4, 0.4],
          [0.6, 0.6, 0.6]]
    CL, CD, CM = Cx, Cx, Cx
    myAirfoil = c81utils.C81('myAirfoil', \
                             alpha, mach, CL, \
                             alpha, mach, CD, \
                             alpha, mach, CM)

    # 'dump' writes a C81 formatted text file
    with open("myAirfoil.C81", "w") as f:
      c81utils.dump(myAirfoil, f)


License and author
-------------------
GPLv3. By `Cibin Joseph <https://github.com/cibinjoseph>`_
