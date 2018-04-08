import unittest
import sqlite3 as db
import pandas as pd
import numpy as np
from quantizer import Quantizer
import quantizer

class TestQuantizer(unittest.TestCase):
    def test_count_obs(self, nrows=10):
        con = db.connect("observations.db")
        q = Quantizer()
        levels = [quantizer.equal_spaced_bounds(3) for i in range(5)]
        levels.append(quantizer.equal_spaced_bounds(2))
        counts_mdarray = q.count_obs(con, levels, nrows)
        if nrows <= 100:
            column_names = ["f1","f2","f3","f4","f5","class"]
            data = pd.read_csv("pr_data", names=column_names, delimiter='\s+', nrows=nrows)
            quantize = quantizer.gen_quantize(levels[0])
            qdata = data.applymap(quantize)
            qdata[column_names[-1]] = qdata[column_names[-1]].apply(lambda e:1 if e==2 else 0)
            for i, row in qdata.iterrows():
                self.assertTrue(counts_mdarray[row]>0)
        con.close()
        return counts_mdarray
    
    def test_calc_prob_dc(self, nrows=10):
        q = Quantizer()
        counts = self.test_count_obs(nrows)
        probsdc = q.calc_prob_dc(counts)
        self.assertAlmostEqual(probsdc.total(), counts.num_levels[-1])
        #self.assertEqual(probsdc.total(), 20.0)#counts.num_levels[-1])
        #totals = [0]*counts.num_levels[-1]
        #for combo in probsdc:
        #    totals[combo[-1]] += probsdc[combo]
        return probsdc
    
    def test_calc_pd(self, nrows=10):
        q = Quantizer()
        counts = self.test_count_obs(nrows)
        p_d = q.calc_pd(counts)
        self.assertEqual(nrows, p_d.total())
        if counts.num_levels[-1] == 2:
            for combination in p_d:
                total = p_d[combination]
                a = counts[combination + [0]]
                b = counts[combination + [1]]
                self.assertEqual(total, a+b)

    def test_equal_spaced_bounds(self):
        equal_bounds = quantizer.equal_spaced_bounds(3, 100)
        expected_output = [0.0, 33.333333333333336, 66.66666666666667]
        self.assertSequenceEqual(equal_bounds, expected_output)

    def test_quantize(self):
        eb = quantizer.equal_spaced_bounds(3, 10)
        quantize = quantizer.gen_quantize(eb)
        self.assertEqual(quantize(-10), 0)
        self.assertEqual(quantize(0), 0)
        self.assertEqual(quantize(1), 0)
        self.assertEqual(quantize(5), 1)
        self.assertEqual(quantize(9.9), 2)
        self.assertEqual(quantize(10), 2)
        self.assertEqual(quantize(15), 2)

    def test_data_to_hash_count(self):
        con = db.connect('observations.db')
        q = Quantizer()
        hash_count = q.data_to_hash_count(con)
        #print len(hash_count)

    def test_dimensional_probabilities(self, nrows=10):
        column_names = ["f1","f2","f3","f4","f5","class"]
        data = pd.read_csv("pr_data", names=column_names, delimiter='\s+', nrows=nrows)
        q = Quantizer()
        probs = q.dimensional_probabilities(data, 2)
        for prob_d in probs:
            self.assertAlmostEqual(sum(prob_d), 1.0)
        return probs
    
    def test_dimensional_entropy(self, nrows=10):
        probs = self.test_dimensional_probabilities(nrows)
        q = Quantizer()
        actual_output = q.dimensional_entropy(probs)
        expected_output = [1.0, 0.8812908992306927, 0.9709505944546688,
                           1.0, 0.9709505944546688, 0.8812908992306927]
        if nrows == 10:
            for ao, eo in zip(actual_output, expected_output):
                self.assertAlmostEqual(ao, eo)
        return actual_output
    
    def test_levels_from_data(self, nrows=10000):
        q = Quantizer()
        column_names = ["f1","f2","f3","f4","f5","class"]
        data = pd.read_csv("pr_data", names=column_names, delimiter='\s+', nrows=nrows)
        eo = q.levels_from_data(data)
        for level in eo:
            self.assertEqual(7, level)
    
    def test_calc_levels(self, nrows=1000):
        de = self.test_dimensional_entropy(nrows)[:-1]
        q = Quantizer()
        actual_output = q.calc_levels(de, 10000)
        #exact_dim_bins = [6.3099749, 6.30885208, 6.30969821,
        #                   6.30984611, 6.30949598]
        for ao in actual_output:
            self.assertEqual(ao, 7)
    
    def test_ksmooth(self, nrows=10000):
        p_dc = self.test_calc_prob_dc(nrows)
        q = Quantizer()
        kstar = np.sqrt(nrows)
        con = db.connect('observations.db')
        bounds = [[0.0, 0.16666666666666666, 0.5666666666666667, 0.5666666666666667, 0.6166666666666667, 0.9166666666666666], [0.0, 0.5, 0.5, 0.55, 0.6166666666666667, 0.6666666666666667], [0.0, 0.1, 0.15000000000000002, 0.25, 0.6000000000000001, 0.9500000000000002], [0.0, 0.25, 0.3333333333333333, 0.7833333333333333, 0.8333333333333333, 0.8333333333333334], [0.0, 0.1, 0.2, 0.5, 0.6, 0.85], [0.0, 0.5]]
        #bounds = [quantizer.equal_spaced_bounds(6) for i in range(5)]
        #bounds.append([0,.5])
        volumes = q.calc_volumes(bounds[:-1])
        counts = q.count_obs(con, bounds, nrows)
        con.close()
        q.ksmooth(counts, volumes, kstar)

    def test_calc_volumes(self):
        levels = [quantizer.equal_spaced_bounds(6) for i in range(5)]
        levels = [[0.0, 0.16666666666666666, 0.5666666666666667, 0.5666666666666667, 0.6166666666666667, 0.9166666666666666], [0.0, 0.5, 0.5, 0.55, 0.6166666666666667, 0.6666666666666667], [0.0, 0.1, 0.15000000000000002, 0.25, 0.6000000000000001, 0.9500000000000002], [0.0, 0.25, 0.3333333333333333, 0.7833333333333333, 0.8333333333333333, 0.8333333333333334], [0.0, 0.1, 0.2, 0.5, 0.6, 0.85], [0.0, 0.5]]
        q = Quantizer()
        q.calc_volumes(levels)

    def runTest(self):
        pass






if __name__=="__main__":
    unittest.main()