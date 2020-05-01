""" Reads XFOIL polar file and writes to C81 format """
""" The mach number is replicated over three columns """
import c81utils
import sys
import numpy as np

def main():
    xfoilFilename = sys.argv[-1]

    with open(xfoilFilename, 'r') as fh:
        lines = fh.readlines()[2:-2]

    airfoilName = lines[0].split(':')[1].strip()
    lines = lines[9:]

    # Extract data values
    alpha = []
    CL = []
    CD = []
    CM = []
    for line in lines:
        cols = line.split()
        alpha.append(float(cols[0]))
        CL.append(float(cols[1]))
        CD.append(float(cols[2]))
        CM.append(float(cols[4]))

    alpha = np.array(alpha)
    CL = np.array(CL)
    CD = np.array(CD)
    CM = np.array(CM)

    mach = np.array([0.0, 0.5, 1.0])
    # Convert CL, CD, CM to 2d arrays
    CL = np.tile(CL, (mach.size,1)).T
    CD = np.tile(CD, (mach.size,1)).T
    CM = np.tile(CM, (mach.size,1)).T

    c81Airfoil = c81utils.C81(airfoilName, \
                             alpha, mach, CL, \
                             alpha, mach, CD, \
                             alpha, mach, CM)
    with open(xfoilFilename + '.C81', 'w') as fh:
        c81utils.dump(c81Airfoil, fh)


if __name__ == '__main__':
    main()
