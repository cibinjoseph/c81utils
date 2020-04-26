.. image:: https://img.shields.io/pypi/v/c81utils.svg
   :target: https://pypi.org/project/c81utils/
   :alt: c81utils on PyPI

.. image:: https://travis-ci.com/cibinjoseph/c81utils.svg?token=FMmn3XQeRECGNsy6mT6B&branch=master
   :target: https://travis-ci.com/cibinjoseph/c81utils

c81utils
=========
A Python module for working with C81 airfoil tables.  

Usage
-------
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


Installation
-------------
*c81utils* is written in Python 3. Use pip to install.

.. code-block:: bash

    pip3 install c81utils


Author
-------
`Cibin Joseph <https://github.com/cibinjoseph>`_
