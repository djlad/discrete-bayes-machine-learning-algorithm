import unittest
from optimizer import Optimizer
import quantizer
import os
#import inputs.equal_bounds

class TestOptimizer(unittest.TestCase):
    def equal_bounds(self):
        levels = [quantizer.equal_spaced_bounds(7) for i in range(5)]
        levels.append(quantizer.equal_spaced_bounds(2))
        return levels

    def best_bounds(self):
        optimal_bounds =    [
        [0.00000,   0.02037,   0.18117,   0.56374,   0.90676,   0.98718,   1.00000],
        [0.00000,   0.47436,   0.49150,   0.53603,   0.58948,   0.62023,   1.00000],
        [0.00000,   0.08321,   0.15193,   0.24154,   0.60653,   0.94493,   1.00000],
        [0.00000,   0.02697,   0.22574,   0.25494,   0.32456,   0.85316,   1.00000],
        [0.00000,   0.06348,   0.10362,   0.19162,   0.51352,   0.60375,   1.00000]]
        optimal_bounds.append(quantizer.equal_spaced_bounds(2))
        return optimal_bounds
    
    def c_bounds(self):
        ob = [[0.0, 0.02, 0.18000000000000002, 0.56, 0.9100000000000001, 0.9900000000000001], [0.0, 0.47000000000000003, 0.49000000000000005, 0.49000000000000005, 0.54, 0.62], [0.0, 0.08, 0.15000000000000002, 0.24, 0.6033333333333333, 0.9433333333333334], [0.0, 0.24, 0.32999999999999996, 0.85, 0.85, 0.8500000000000001], [0.0, 0.08, 0.19, 0.51, 0.6, 1.0], [0.0, 0.5]]
        return ob

    def create_optimizer(self):
        return Optimizer()
    
    def test_eval_bounds(self, nrows=100000, offset=3300000, trainoffset=0):
        op = self.create_optimizer()
        tb = self.best_bounds()
        #tb = self.equal_bounds()
        #tb = self.c_bounds()
        kstar = 0
        ev = op.eval_bounds(tb, nrows, offset, trainoffset, kstar)
        print kstar
        print ev
    
    def test_optimize_bounds(self):
        op = self.create_optimizer()
        bounds = self.equal_bounds()
        #bounds = self.c_bounds()
        #config = inputs.equal_bounds.input
        ctext = read_input('e_bounds1.txt')
        config = eval(ctext)
        op.optimize_bounds(config)
    
    def test_probability_convergence(self):
        for i in range(50):
            self.test_eval_bounds(i*2000)



def read_input(file_name):
    f = open(os.path.join('inputs', file_name), 'r')
    txt = f.read()
    f.close()
    return txt

if __name__ == "__main__":
    unittest.main()