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

    def create_optimizer(self):
        return Optimizer()
    
    def test_eval_bounds(self, nrows=1000):
        op = self.create_optimizer()
        equal_bounds = self.equal_bounds()
        op.eval_bounds(equal_bounds)
    
    def test_optimize_bounds(self):
        op = self.create_optimizer()
        equal_bounds = self.equal_bounds()
        op.optimize_bounds(equal_bounds)


if __name__ == "__main__":
    unittest.main()