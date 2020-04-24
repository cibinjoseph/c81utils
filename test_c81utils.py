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

class C81TestGood(unittest.TestCase):

    def setUp(self):
        self.npl = c81utils.C81(testdir + 'sample1.C81')

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
        self.npl2 = c81utils.C81(testdir + 'sample1.C81')
        self.assertTrue(self.npl == self.npl2)



if __name__ == '__main__':
    unittest.main()
