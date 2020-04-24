import numpy as np
from scipy.interpolate import RectBivariateSpline


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
    isEmpty = True

    def __init__(self, airfoilname, \
                 alpha_l, mach_l, cl, \
                 alpha_d, mach_d, cd, \
                 alpha_m, mach_m, cm):

        self._checkdatatype(airfoilname, \
                            alpha_l=alpha_l, mach_l=mach_l, cl=cl,
                            alpha_d=alpha_d, mach_d=mach_d, cd=cd,
                            alpha_m=alpha_m, mach_m=mach_m, cm=cm)

        self.isEmpty = False
        self.airfoilname = airfoilname
        self.cl = CoeffTable(np.array(alpha_l), np.array(mach_l), np.array(cl))
        self.cd = CoeffTable(np.array(alpha_d), np.array(mach_d), np.array(cd))
        self.cm = CoeffTable(np.array(alpha_m), np.array(mach_m), np.array(cm))

        self.cl.checkdim('CL')
        self.cd.checkdim('CD')
        self.cm.checkdim('CM')

        self._interpCL = RectBivariateSpline( self.cl.alpha, self.cl.mach, \
                                            self.cl.val, kx=1, ky=1)
        self._interpCD = RectBivariateSpline( self.cd.alpha, self.cd.mach, \
                                            self.cd.val, kx=1, ky=1)
        self._interpCM = RectBivariateSpline( self.cm.alpha, self.cm.mach, \
                                            self.cm.val, kx=1, ky=1)


    def __repr__(self):
        if not self.isEmpty:
            strout = ('C81 dataset ' +
                      '\n  Airfoil name : ' + self.airfoilname +
                      '\n  CL data size: ' + str(np.shape(self.cl.val)[0]) + ' by ' + str(np.shape(self.cl.val)[1]) +
                      '\n  CD data size: ' + str(np.shape(self.cd.val)[0]) + ' by ' + str(np.shape(self.cd.val)[1]) +
                      '\n  CM data size: ' + str(np.shape(self.cm.val)[0]) + ' by ' + str(np.shape(self.cm.val)[1]))
        else:
            strout = 'Uninitialized C81 class'
        return strout

    def __eq__(self, other):
        ret = []
        ret.append([self.cl.alpha.tolist() == other.cl.alpha.tolist()])
        ret.append([self.cl.mach.tolist() == other.cl.mach.tolist()])
        ret.append(self.cl.val.tolist() == other.cl.val.tolist())
        return all(ret)

    @staticmethod
    def _checkdatatype(airfoilname, **kwargs):
        """
        Checks data type of variables
        Arguments may be in any order but should be keyworded except for airfoilname
        Eg: naca._checkdatatype('NACA', mach_l=[], alpha_l=[], cl=[],
                                        mach_d=[], alpha_d=[], cd=[],
                                        mach_m=[], alpha_m=[], cm=[])
        Returns a dict with keys as var names and values as a bool
        """
        if len(kwargs) != 9:
            raise TypeError('_checkdatatype() takes 10 input arguments')

        for key in kwargs:
            if not isinstance(kwargs[key], (list, np.ndarray)):
                raise TypeError('The input argument ' + key + 'is of incorrect data type')

        if not isinstance(airfoilname, str):
            raise TypeError('The input argument airfoilname is of incorrect data type')

    def getCL(self, alphaQuery, machQuery):
        """ Returns bilinearly interpolated CL value """
        return self._interpCL(alphaQuery, machQuery)[0][0]

    def getCD(self, alphaQuery, machQuery):
        """ Returns bilinearly interpolated CD value """
        return self._interpCD(alphaQuery, machQuery)[0][0]

    def getCM(self, alphaQuery, machQuery):
        """ Returns bilinearly interpolated CM value """
        return self._interpCM(alphaQuery, machQuery)[0][0]

def load(fileObject):
    """ Read C81 formatted data from text file """
    header = fileObject.readline().rstrip()
    airfoilname = header[0:30]
    nmach_l = int(header[30:32])
    nalpha_l = int(header[32:34])
    nmach_d = int(header[34:36])
    nalpha_d = int(header[36:38])
    nmach_m = int(header[38:40])
    nalpha_m = int(header[40:42])

    # LIFT
    multilinedata = nmach_l >= 9
    # Read mach values
    mach_l = fileObject.readline().rstrip()
    if multilinedata:
        mach_l = mach_l + fileObject.readline().rstrip()
    mach_l = list(map(float, mach_l.split()))
    # Read alpha and coeff. values
    alpha_l = []
    cl = []
    for i in range(nalpha_l):
        line = fileObject.readline().rstrip()
        if multilinedata:
            line = line + fileObject.readline().rstrip()
        line = list(map(float, line.split()))
        alpha_l = alpha_l + [line[0]]
        cl = cl + [line[1:]]

    # DRAG
    multilinedata = nmach_d >= 9
    # Read mach values
    mach_d = fileObject.readline().rstrip()
    if multilinedata:
        mach_d = mach_d + fileObject.readline().rstrip()
    mach_d = list(map(float, mach_d.split()))
    # Read alpha and coeff. values
    alpha_d = []
    cd = []
    for i in range(nalpha_d):
        line = f.readline().rstrip()
        if multilinedata:
            line = line + fileObject.readline().rstrip()
        line = list(map(float, line.split()))
        alpha_d = alpha_d + [line[0]]
        cd = cd + [line[1:]]

    # MOMENT
    multilinedata = nmach_m >= 9
    # Read mach values
    mach_m = fileObject.readline().rstrip()
    if multilinedata:
        mach_m = mach_m + fileObject.readline().rstrip()
    mach_m = list(map(float, mach_m.split()))
    # Read alpha and coeff. values
    alpha_m = []
    cm = []
    for i in range(nalpha_m):
        line = fileObject.readline().rstrip()
        if multilinedata:
            line = line + fileObject.readline().rstrip()
        line = list(map(float, line.split()))
        alpha_m = alpha_m + [line[0]]
        cm = cm + [line[1:]]

    return C81(airfoilname, \
                alpha_l, mach_l, cl, \
                alpha_d, mach_d, cd, \
                alpha_m, mach_m, cm)


a = [0, 2, 8, 10]    # rows
m = [0.0, 0.5, 1.0]  # columns
c = [[0, 0.1, 0.2], [0.2, 0.3, 0.4], [0.8, 0.9, 1.0], [1.0, 1.1, 1.2]]

naca = C81('NACA 0012', a, m, c, a, m, c, a, m, c)
print(naca.getCL(2, 2.0))
# aQ = np.array([0, 2, 10, 8])
# mQ = np.array([0, 0.5, 1, 0])

# f = open('sample1.C81')
# naca = load(f)
# f.close()
