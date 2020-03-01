import unittest
import c81utils
import numpy as np

testdir = 'tests/'

class CoeffTableTestGood(unittest.TestCase):

    def setUp(self):
        f = open(testdir + 'table1.txt','r')
        self.mach = list(map(float, f.readline().rstrip().split()))
        self.alpha = list(map(float, f.readline().rstrip().split()))
        self.val = []
        for line in f.readlines():
            self.val.append(list(map(float, line.rstrip().split())))
        f.close()

        self.mach = np.array(self.mach)
        self.alpha = np.array(self.alpha)
        self.val = np.array(self.val)

        self.cl = c81utils.CoeffTable(self.mach, self.alpha, self.val)

    def test_init(self):
        self.assertListEqual(self.cl.mach.tolist(),self.mach.tolist())
        self.assertListEqual(self.cl.alpha.tolist(),self.alpha.tolist())
        self.assertListEqual(self.cl.val.tolist(),self.val.tolist())


class CoeffTableTestBad(unittest.TestCase):

    def setUp(self):
        f = open(testdir + 'table1.txt','r')
        self.mach = list(map(float, f.readline().rstrip().split()))
        self.alpha = list(map(float, f.readline().rstrip().split()))
        self.val = []
        for line in f.readlines():
            self.val.append(list(map(float, line.rstrip().split())))
        f.close()

        self.mach = np.array(self.mach + [1.5])
        self.alpha = np.array(self.alpha)
        self.val = np.array(self.val)

        self.cl = c81utils.CoeffTable(self.mach, self.alpha, self.val)

    def test_init(self):
        self.assertListEqual(self.cl.mach.tolist(),self.mach.tolist())
        self.assertListEqual(self.cl.alpha.tolist(),self.alpha.tolist())
        self.assertListEqual(self.cl.val.tolist(),self.val.tolist())

    def test_checkdim(self):
        self.assertRaises(ValueError, self.cl.checkdim, 'cl')

class C81TestGood(unittest.TestCase):

    def setUp(self):
        self.npl = c81utils.C81(testdit + 'sample1.C81')

if __name__ == '__main__':
    unittest.main()
