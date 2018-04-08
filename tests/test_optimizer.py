import unittest
from optimizer import Optimizer
import quantizer

class TestOptimizer(unittest.TestCase):
    def equal_bounds(self):
        levels = [quantizer.equal_spaced_bounds(6) for i in range(5)]
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
        ob = [[0.0, 0.16666666666666666, 0.5666666666666667, 0.5666666666666667, 0.6166666666666667, 0.9166666666666666], [0.0, 0.5, 0.5, 0.55, 0.6166666666666667, 0.6666666666666667], [0.0, 0.1, 0.15000000000000002, 0.25, 0.6000000000000001, 0.9500000000000002], [0.0, 0.25, 0.3333333333333333, 0.7833333333333333, 0.8333333333333333, 0.8333333333333334], [0.0, 0.1, 0.2, 0.5, 0.6, 0.85], [0.0, 0.5]]
        return ob

    def create_optimizer(self):
        return Optimizer()
    
    def test_eval_bounds(self, nrows=50000, offset=3300000, trainoffset=0):
        op = self.create_optimizer()
        tb = self.best_bounds()
        tb = self.equal_bounds()
        tb = self.c_bounds()
        ev = op.eval_bounds(tb, nrows, offset, trainoffset)
        print(ev)

    
    def test_optimize_bounds(self):
        op = self.create_optimizer()
        bounds = self.equal_bounds()
        #bounds = self.c_bounds()
        op.optimize_bounds(bounds)


if __name__ == "__main__":
    unittest.main()