import numpy as np
from scipy.interpolate import RectBivariateSpline


__version__ = '1.0.4'

class CoeffTable:
    """ CoeffTable class for aerodynamic coefficients """

    alpha = np.array([])
    mach = np.array([])
    val = np.array([])

    def __init__(self, alpha, mach, val):
        self.alpha = alpha
        self.mach = mach
        self.val = val

    def checkdim(self, coeffname):
        """ Checks dimensions and consistency in variables """
        if len(self.mach.shape) != 1:
            raise ValueError('Wrong dimensions for ' + coeffname + ' mach')
        if len(self.alpha.shape) != 1:
            raise ValueError('Wrong dimensions for ' + coeffname + ' alpha')
        if len(self.val.shape) != 2:
            raise ValueError('Wrong dimensions for ' + coeffname + ' coefficient matrix')

        cols = self.mach.shape[0]
        rows = self.alpha.shape[0]
        if self.val.shape[0] != rows:
            raise ValueError('Inconsistent no. of alpha and ' + coeffname + ' coefficient values')
        elif self.val.shape[1] != cols:
            raise ValueError('Inconsistent no. of mach and ' + coeffname + ' coefficient values')

class C81:
    """ C81 class for c81 formatted airfoil tables """

    def __init__(self, airfoilname, \
                 alpha_L, mach_l, CL, \
                 alpha_D, mach_d, CD, \
                 alpha_M, mach_m, CM):

        self._checkdatatype(airfoilname, \
                            alpha_L=alpha_L, mach_l=mach_l, CL=CL,
                            alpha_D=alpha_D, mach_d=mach_d, CD=CD,
                            alpha_M=alpha_M, mach_m=mach_m, CM=CM)

        self.airfoilname = airfoilname
        self.CL = CoeffTable(np.array(alpha_L), np.array(mach_l), np.array(CL))
        self.CD = CoeffTable(np.array(alpha_D), np.array(mach_d), np.array(CD))
        self.CM = CoeffTable(np.array(alpha_M), np.array(mach_m), np.array(CM))

        self.CL.checkdim('CL')
        self.CD.checkdim('CD')
        self.CM.checkdim('CM')

        self.refreshInterpolation()

    def __repr__(self):
        strout = ('C81 dataset ' +
                  '\n  Airfoil name : ' + self.airfoilname +
                  '\n  CL data size: ' + str(np.shape(self.CL.val)[0]) + ' by ' + str(np.shape(self.CL.val)[1]) +
                  '\n  CD data size: ' + str(np.shape(self.CD.val)[0]) + ' by ' + str(np.shape(self.CD.val)[1]) +
                  '\n  CM data size: ' + str(np.shape(self.CM.val)[0]) + ' by ' + str(np.shape(self.CM.val)[1]))
        return strout

    def __eq__(self, other):
        ret = []
        ret.append([self.CL.alpha.tolist() == other.CL.alpha.tolist()])
        ret.append([self.CL.mach.tolist() == other.CL.mach.tolist()])
        ret.append(self.CL.val.tolist() == other.CL.val.tolist())
        return all(ret)

    @staticmethod
    def _checkdatatype(airfoilname, **kwargs):
        """
        Checks data type of variables
        Arguments may be in any order but should be keyworded except for airfoilname
        Eg: naca._checkdatatype('NACA', mach_l=[], alpha_L=[], CL=[],
                                        mach_d=[], alpha_D=[], CD=[],
                                        mach_m=[], alpha_M=[], CM=[])
        Returns a dict with keys as var names and values as a bool
        """
        if len(kwargs) != 9:
            raise TypeError('_checkdatatype() takes 10 input arguments')

        for key in kwargs:
            if not isinstance(kwargs[key], (list, np.ndarray)):
                raise TypeError('The input argument ' + key + 'is of incorrect data type')

        if not isinstance(airfoilname, str):
            raise TypeError('The input argument airfoilname is of incorrect data type')

    @staticmethod
    def _isIncreasing(arr):
        """ Checks if monotonically increasing array """
        return np.all(np.diff(arr) > 0)

    def refreshInterpolation(self):
        """ Refreshes the interpolating functions. """
        """ May be used when data has been changed manually. """
        # Ensure alpha and mach are strictly increasing
        if not self._isIncreasing(self.CL.alpha):
            raise ValueError('alpha CL should be strictly increasing')
        if not self._isIncreasing(self.CL.mach):
            raise ValueError('mach CL should be strictly increasing')
        if not self._isIncreasing(self.CD.alpha):
            raise ValueError('alpha CL should be strictly increasing')
        if not self._isIncreasing(self.CD.mach):
            raise ValueError('mach CL should be strictly increasing')
        if not self._isIncreasing(self.CM.alpha):
            raise ValueError('alpha CL should be strictly increasing')
        if not self._isIncreasing(self.CM.mach):
            raise ValueError('mach CL should be strictly increasing')

        self._interpCL = RectBivariateSpline( self.CL.alpha, self.CL.mach, \
                                            self.CL.val, kx=1, ky=1)
        self._interpCD = RectBivariateSpline( self.CD.alpha, self.CD.mach, \
                                            self.CD.val, kx=1, ky=1)
        self._interpCM = RectBivariateSpline( self.CM.alpha, self.CM.mach, \
                                            self.CM.val, kx=1, ky=1)

    def getCL(self, alphaQuery, machQuery):
        """ Returns bilinearly interpolated CL value """
        return self._interpCL(alphaQuery, machQuery)[0][0]

    def getCD(self, alphaQuery, machQuery):
        """ Returns bilinearly interpolated CD value """
        return self._interpCD(alphaQuery, machQuery)[0][0]

    def getCM(self, alphaQuery, machQuery):
        """ Returns bilinearly interpolated CM value """
        return self._interpCM(alphaQuery, machQuery)[0][0]

def dump(c81Data, fileObject):
    """ Write airfoil tables to C81 formatted file """
    lengths = ''
    lengths = lengths + '{:02d}'.format(c81Data.CL.mach.size)
    lengths = lengths + '{:02d}'.format(c81Data.CL.alpha.size)
    lengths = lengths + '{:02d}'.format(c81Data.CD.mach.size)
    lengths = lengths + '{:02d}'.format(c81Data.CD.alpha.size)
    lengths = lengths + '{:02d}'.format(c81Data.CM.mach.size)
    lengths = lengths + '{:02d}'.format(c81Data.CM.alpha.size)

    # Header
    line = '{:30.30}{:12.12}'.format(c81Data.airfoilname, lengths)
    fileObject.write(line + '\n')

    spaces7 = '       '

    def wrapline(lineString, chars=70):
        if len(lineString) > chars:
            return lineString[:chars] + '\n' + spaces7 + lineString[chars:]
        else:
            return lineString

    # Lift section
    line = spaces7
    for val in c81Data.CL.mach:
        line += '{:7.3f}'.format(val)
    line = wrapline(line)
    fileObject.write(line + '\n')
    for indx, val in enumerate(c81Data.CL.alpha):
        line = '{:7.2f}'.format(val)
        for CLval in c81Data.CL.val[indx]:
            line += '{:7.3f}'.format(CLval)
        line = wrapline(line)
        fileObject.write(line + '\n')

    # Drag section
    line = spaces7
    for val in c81Data.CD.mach:
        line += '{:7.3f}'.format(val)
    line = wrapline(line)
    fileObject.write(line + '\n')
    for indx, val in enumerate(c81Data.CD.alpha):
        line = '{:7.2f}'.format(val)
        for CDval in c81Data.CD.val[indx]:
            line += '{:7.3f}'.format(CDval)
        line = wrapline(line)
        fileObject.write(line + '\n')

    # Moment section
    line = spaces7
    for val in c81Data.CM.mach:
        line += '{:7.3f}'.format(val)
    line = wrapline(line)
    fileObject.write(line + '\n')
    for indx, val in enumerate(c81Data.CM.alpha):
        line = '{:7.2f}'.format(val)
        for CMval in c81Data.CM.val[indx]:
            line += '{:7.3f}'.format(CMval)
        line = wrapline(line)
        fileObject.write(line + '\n')


def load(fileObject):
    """ Read airfoil tables from C81 formatted file """
    header = fileObject.readline().rstrip()
    airfoilname = header[0:30]
    nmach_l = int(header[30:32])
    nalpha_L = int(header[32:34])
    nmach_d = int(header[34:36])
    nalpha_D = int(header[36:38])
    nmach_m = int(header[38:40])
    nalpha_M = int(header[40:42])

    # LIFT
    multilinedata = nmach_l >= 9
    # Read mach values
    mach_l = fileObject.readline().rstrip()
    if multilinedata:
        mach_l = mach_l + fileObject.readline().rstrip()
    mach_l = list(map(float, mach_l.split()))
    # Read alpha and coeff. values
    alpha_L = []
    CL = []
    for i in range(nalpha_L):
        line = fileObject.readline().rstrip()
        if multilinedata:
            line = line + fileObject.readline().rstrip()
        line = list(map(float, line.split()))
        alpha_L = alpha_L + [line[0]]
        CL = CL + [line[1:]]

    # DRAG
    multilinedata = nmach_d >= 9
    # Read mach values
    mach_d = fileObject.readline().rstrip()
    if multilinedata:
        mach_d = mach_d + fileObject.readline().rstrip()
    mach_d = list(map(float, mach_d.split()))
    # Read alpha and coeff. values
    alpha_D = []
    CD = []
    for i in range(nalpha_D):
        line = fileObject.readline().rstrip()
        if multilinedata:
            line = line + fileObject.readline().rstrip()
        line = list(map(float, line.split()))
        alpha_D = alpha_D + [line[0]]
        CD = CD + [line[1:]]

    # MOMENT
    multilinedata = nmach_m >= 9
    # Read mach values
    mach_m = fileObject.readline().rstrip()
    if multilinedata:
        mach_m = mach_m + fileObject.readline().rstrip()
    mach_m = list(map(float, mach_m.split()))
    # Read alpha and coeff. values
    alpha_M = []
    CM = []
    for i in range(nalpha_M):
        line = fileObject.readline().rstrip()
        if multilinedata:
            line = line + fileObject.readline().rstrip()
        line = list(map(float, line.split()))
        alpha_M = alpha_M + [line[0]]
        CM = CM + [line[1:]]

    return C81(airfoilname, \
                alpha_L, mach_l, CL, \
                alpha_D, mach_d, CD, \
                alpha_M, mach_m, CM)
