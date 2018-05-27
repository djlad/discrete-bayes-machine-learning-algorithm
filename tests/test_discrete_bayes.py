import unittest
import math
import pandas as pd
import numpy as np
import discrete_bayes as dbayes
from discrete_bayes import DiscreteBayes
from test_quantizer import TestQuantizer
from quantizer import Quantizer
import quantizer
import sqlite3 as dbs
import mdarray as md

class TestDiscreteBayes(unittest.TestCase):
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

    def create_discrete_bayes(self):
        return DiscreteBayes(np.identity(2))
    
    def create_test_quantizer(self):
        return TestQuantizer()
    
    def create_quantizer(self):
        return Quantizer()

    def test_calc_prob_cd(self, nrows=100000):
        db = self.create_discrete_bayes()
        tq = self.create_test_quantizer()
        q = Quantizer()
        counts = tq.test_count_obs(nrows)
        p_dc = q.calc_prob_dc(counts)
        p_d = q.calc_pd(p_dc)
        p_cd = db.calc_prob_cd(p_dc, p_d, [.5, .5])
    
    def test_optimal_bounds(self, nrows=1000, offset=3300000):
        db = self.create_discrete_bayes()
        q = self.create_quantizer()

        levels = self.equal_bounds()
        levels = self.best_bounds()
        #print levels

        con = dbs.connect("observations.db")
        counts = q.count_obs(con, levels, nrows)
        con.close()
        p_dc = q.calc_prob_dc(counts)
        p_d = q.calc_pd(p_dc)
        p_cd = db.calc_prob_cd(p_dc, p_d, [.5, .5])
        '''
        print p_cd[[5, 5, 5, 5, 5, 1]]
        print p_cd[[5, 5, 5, 5, 5, 0]]
        d_rules, e_gains = db.bayes_d_rule(p_cd)
        print d_rules[[5,5,5,5,5]]
        print e_gains[[5,5,5,5,5]]
        '''
        '''
        for com in d_rules:
            print com
            print d_rules[com]
            print e_gains[com]
            print p_cd[com + [0]]
            print p_cd[com + [1]]
        '''
        con = dbs.connect("observations.db")
        test_counts = q.count_obs(con, levels, nrows, offset)
        con.close()
    
    def test_confusion_matrix(self, nrows=1000, offset=3300000): 
        db = self.create_discrete_bayes()
        q = self.create_quantizer()
        levels = self.equal_bounds()
        #levels = self.best_bounds()
        con = dbs.connect("observations.db")
        counts = q.count_obs(con, levels, nrows)
        con.close()
        p_dc = q.calc_prob_dc(counts)
        p_d = q.calc_pd(p_dc)
        p_cd = db.calc_prob_cd(p_dc, p_d, [.5, .5])
        con.close()
        drules, e_gains = db.bayes_d_rule(p_cd)
        con = dbs.connect("observations.db")
        test_counts = q.count_obs(con, levels, nrows, offset)
        con.close()
        tc = test_counts
        cm = db.confusion_matrix(drules, test_counts)

        gain = db.calc_gain(cm, db.gain_matrix)
        true_assigned = db.eval_rules(drules, test_counts)[-1]
        self.assertAlmostEqual(gain, true_assigned)
        
    def test_drules_class_assignment(self):
        #input probabilities from class
        p_dc_ar = [[.12,.18,.3],[.2,.16,.04]]
        e = [[1,0],[0,2]]
        db = DiscreteBayes(e)
        q = self.create_quantizer()
        p_dc = md.Mdarray([3, 2])
        for i in p_dc:
            p_dc[i] = p_dc_ar[i[1]][i[0]]
        p_d = q.calc_pd(p_dc)
        p_cd = db.calc_prob_cd(p_dc, p_d, [.6, .4])
        d_rules, e_gains = db.bayes_d_rule(p_cd)
        print 'p_dc'
        print p_dc
        print 'p_d'
        print p_d
        print 'p_cd'
        print p_cd
        print 'd_rules'
        print d_rules
        print 'e_gains'
        print e_gains

        test_data = md.Mdarray([3,2])
        for i in test_data:
            test_data[i] = p_dc_ar[i[1]][i[0]]*100
        print 'test data'
        print test_data
        print 'confusion matrix'
        cm = db.confusion_matrix(d_rules, test_data)
        print cm
        print 'gain'
        print db.calc_gain(e, cm)




if __name__ == "__main__":
    unittest.main()

