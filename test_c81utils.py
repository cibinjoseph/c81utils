import unittest
import c81utils
import numpy as np
import csv

testdir = 'tests/'

class CoeffTableTestGood(unittest.TestCase):

    def setUp(self):
        f = open(testdir + 'table1.csv', 'r')
        self.mach = list(map(float, f.readline().rstrip().split()))
        self.alpha = list(map(float, f.readline().rstrip().split()))
        self.val = []
        for line in f.readlines():
            self.val.append(list(map(float, line.rstrip().split())))
        f.close()

        self.mach = np.array(self.mach)
        self.alpha = np.array(self.alpha)
        self.val = np.array(self.val)

        self.cl = c81utils.CoeffTable(self.alpha, self.mach, self.val)

    def test_init(self):
        self.assertListEqual(self.cl.alpha.tolist(), self.alpha.tolist())
        self.assertListEqual(self.cl.mach.tolist(), self.mach.tolist())
        self.assertListEqual(self.cl.val.tolist(), self.val.tolist())


class CoeffTableTestBad(unittest.TestCase):

    def setUp(self):
        f = open(testdir + 'table1.csv', 'r')
        self.mach = list(map(float, f.readline().rstrip().split()))
        self.alpha = list(map(float, f.readline().rstrip().split()))
        self.val = []
        for line in f.readlines():
            self.val.append(list(map(float, line.rstrip().split())))
            f.close()

        self.mach = np.array(self.mach + [1.5])
        self.alpha = np.array(self.alpha)
        self.val = np.array(self.val)

        self.cl = c81utils.CoeffTable(self.alpha, self.mach, self.val)

    def test_init(self):
        self.assertListEqual(self.cl.alpha.tolist(), self.alpha.tolist())
        self.assertListEqual(self.cl.mach.tolist(), self.mach.tolist())
        self.assertListEqual(self.cl.val.tolist(), self.val.tolist())

    def test_checkdim(self):
        self.assertRaises(ValueError, self.cl.checkdim, 'cl')

class C81FileTestGood(unittest.TestCase):

    def setUp(self):
        with open(testdir + 'sample1.C81') as f:
            self.npl = c81utils.load(f)

        # Lift
        f = open(testdir + 'sample1_CL.csv', 'r')
        self.val_l = list(csv.reader(f, delimiter=' '))
        f.close()

        self.mach_l = self.val_l.pop(0)
        del self.mach_l[0]
        self.alpha_l = [i[0] for i in self.val_l]
        for i in range(len(self.alpha_l)):
            del self.val_l[i][0]
            self.val_l[i] = list(map(float, self.val_l[i]))

        self.mach_l = list(map(float, self.mach_l))
        self.alpha_l = list(map(float, self.alpha_l))

        # Drag
        f = open(testdir + 'sample1_CD.csv', 'r')
        self.val_d = list(csv.reader(f, delimiter=' '))
        f.close()

        self.mach_d = self.val_d.pop(0)
        del self.mach_d[0]
        self.alpha_d = [i[0] for i in self.val_d]
        for i in range(len(self.alpha_d)):
            del self.val_d[i][0]
            self.val_d[i] = list(map(float, self.val_d[i]))

        self.mach_d = list(map(float, self.mach_d))
        self.alpha_d = list(map(float, self.alpha_d))

        # Moment
        f = open(testdir + 'sample1_CM.csv', 'r')
        self.val_m = list(csv.reader(f, delimiter=' '))
        f.close()

        self.mach_m = self.val_m.pop(0)
        del self.mach_m[0]
        self.alpha_m = [i[0] for i in self.val_m]
        for i in range(len(self.alpha_m)):
            del self.val_m[i][0]
            self.val_m[i] = list(map(float, self.val_m[i]))

        self.mach_m = list(map(float, self.mach_m))
        self.alpha_m = list(map(float, self.alpha_m))

    def test_init(self):
        self.assertListEqual(self.npl.cl.alpha.tolist(), self.alpha_l)
        self.assertListEqual(self.npl.cl.mach.tolist(), self.mach_l)
        self.assertListEqual(self.npl.cl.val.tolist(), self.val_l)

    def test_eq(self):
        with open(testdir + 'sample1.C81') as f:
            self.npl2 = c81utils.load(f)
        self.assertTrue(self.npl == self.npl2)

class C81InputTestGood(unittest.TestCase):

    def setUp(self):
        alpha = [0, 2, 8, 10]
        mach = [0, 0.5, 1]
        coeff = [[0.0, 0.1, 0.2], \
                      [0.2, 0.3, 0.4], \
                      [0.8, 0.9, 1.0], \
                      [1.0, 1.1, 1.2]]
        self.airfoil = c81utils.C81('NACA XXXX', \
                                    alpha, mach, coeff, \
                                    alpha, mach, coeff, \
                                    alpha, mach, coeff)

    def test_singleCoeffs(self):
        # Present values
        CL = self.airfoil.getCL(2, 0.5)
        CD = self.airfoil.getCD(2, 0.5)
        CM = self.airfoil.getCM(2, 0.5)
        self.assertEqual(CL, 0.3)
        self.assertEqual(CL, 0.3)
        self.assertEqual(CL, 0.3)
        CL = self.airfoil.getCL(2, 0.0)
        CD = self.airfoil.getCD(2, 0.0)
        CM = self.airfoil.getCM(2, 0.0)
        self.assertEqual(CL, 0.2)
        self.assertEqual(CD, 0.2)
        self.assertEqual(CM, 0.2)
        # Above limits
        CL = self.airfoil.getCL(8, 1.5)
        CD = self.airfoil.getCD(8, 1.5)
        CM = self.airfoil.getCM(8, 1.5)
        self.assertEqual(CL, 1.0)
        self.assertEqual(CD, 1.0)
        self.assertEqual(CM, 1.0)
        CL = self.airfoil.getCL(16, 0.5)
        CD = self.airfoil.getCD(16, 0.5)
        CM = self.airfoil.getCM(16, 0.5)
        self.assertEqual(CL, 1.1)
        self.assertEqual(CD, 1.1)
        self.assertEqual(CM, 1.1)
        # Below limits
        CL = self.airfoil.getCL(-1, 0.5)
        CD = self.airfoil.getCD(-1, 0.5)
        CM = self.airfoil.getCM(-1, 0.5)
        self.assertEqual(CL, 0.1)
        self.assertEqual(CD, 0.1)
        self.assertEqual(CM, 0.1)
        # 2d interpolated
        CL = self.airfoil.getCL(1, 0.25)
        CD = self.airfoil.getCD(1, 0.25)
        CM = self.airfoil.getCM(1, 0.25)
        self.assertAlmostEqual(CL, 0.15, places=12)
        self.assertAlmostEqual(CD, 0.15, places=12)
        self.assertAlmostEqual(CM, 0.15, places=12)

    def test_arrayCoeffs(self):
        alphas = [2, 2, 8, 16, -1, 1]
        machs = [0.5, 0.0, 1.5, 0.5, 0.5, 0.25]
        CL = list(map(self.airfoil.getCL, alphas, machs))
        CD = list(map(self.airfoil.getCL, alphas, machs))
        CM = list(map(self.airfoil.getCL, alphas, machs))
        correct = [0.3, 0.2, 1.0, 1.1, 0.1, 0.15]
        for indx, val in enumerate(CL):
            self.assertAlmostEqual(val, correct[indx], places=12)
        for indx, val in enumerate(CD):
            self.assertAlmostEqual(val, correct[indx], places=12)
        for indx, val in enumerate(CM):
            self.assertAlmostEqual(val, correct[indx], places=12)


if __name__ == '__main__':
    unittest.main()
