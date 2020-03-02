import numpy as np


# from scipy import interpolate


class CoeffTable:
    """
    CoeffTable class for aerodynamic coefficients
    """
    mach = np.array([])
    alpha = np.array([])
    val = np.array([])

    def __init__(self, mach, alpha, val):
        self.mach = mach
        self.alpha = alpha
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
    """
    C81 class for c81 formatted airfoil tables
    """
    isEmpty = True

    def __init__(self, filename=False):
        if filename:
            self.readfile(filename)

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
        ret = [self.cl.mach.tolist() == other.cl.mach.tolist()]
        ret.append(self.cl.alpha.tolist() == other.cl.alpha.tolist())
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

    @staticmethod
    def _toarray(li):
        """ Returns np.array when a list or np.array is provided as input """
        if isinstance(li, list):
            return np.array(li)
        else:
            return li

    def input(self, airfoilname, mach_l, alpha_l, cl, mach_d, alpha_d, cd, mach_m, alpha_m, cm):
        """ Input airfoil data into C81 class variables as arguments """
        self._checkdatatype(airfoilname,
                            mach_l=mach_l, alpha_l=alpha_l, cl=cl,
                            mach_d=mach_d, alpha_d=alpha_d, cd=cd,
                            mach_m=mach_m, alpha_m=alpha_m, cm=cm)

        self.isEmpty = False
        self.airfoilname = airfoilname
        self.cl = CoeffTable(self._toarray(mach_l), self._toarray(alpha_l), self._toarray(cl))
        self.cd = CoeffTable(self._toarray(mach_d), self._toarray(alpha_d), self._toarray(cd))
        self.cm = CoeffTable(self._toarray(mach_m), self._toarray(alpha_m), self._toarray(cm))

        self.cl.checkdim('CL')
        self.cd.checkdim('CD')
        self.cm.checkdim('CM')

    def readfile(self, filename):
        """ Read C81 formatted data from text file """
        f = open(filename, 'r')
        header = f.readline().rstrip()
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
        mach_l = f.readline().rstrip()
        if multilinedata:
            mach_l = mach_l + f.readline().rstrip()
        mach_l = list(map(float, mach_l.split()))
        # Read alpha and coeff. values
        alpha_l = []
        cl = []
        for i in range(nalpha_l):
            line = f.readline().rstrip()
            if multilinedata:
                line = line + f.readline().rstrip()
            line = list(map(float, line.split()))
            alpha_l = alpha_l + [line[0]]
            cl = cl + [line[1:]]

        # DRAG
        multilinedata = nmach_d >= 9
        # Read mach values
        mach_d = f.readline().rstrip()
        if multilinedata:
            mach_d = mach_d + f.readline().rstrip()
        mach_d = list(map(float, mach_d.split()))
        # Read alpha and coeff. values
        alpha_d = []
        cd = []
        for i in range(nalpha_d):
            line = f.readline().rstrip()
            if multilinedata:
                line = line + f.readline().rstrip()
            line = list(map(float, line.split()))
            alpha_d = alpha_d + [line[0]]
            cd = cd + [line[1:]]

        # MOMENT
        multilinedata = nmach_m >= 9
        # Read mach values
        mach_m = f.readline().rstrip()
        if multilinedata:
            mach_m = mach_m + f.readline().rstrip()
        mach_m = list(map(float, mach_m.split()))
        # Read alpha and coeff. values
        alpha_m = []
        cm = []
        for i in range(nalpha_m):
            line = f.readline().rstrip()
            if multilinedata:
                line = line + f.readline().rstrip()
            line = list(map(float, line.split()))
            alpha_m = alpha_m + [line[0]]
            cm = cm + [line[1:]]
        f.close()

        self.input(airfoilname, mach_l, alpha_l, cl, mach_d, alpha_d, cd, mach_m, alpha_m, cm)


naca = C81()  # Initialize C81 object
a = [10, 20]
m = [0.0, 1.0]
c = [[0.0, 1.0], [0.5, 1.5]]

# naca.input('NACA 0012', a, m, c, a, m, c, a, m, c)
# print(naca)
naca.readfile('sample1.C81')
