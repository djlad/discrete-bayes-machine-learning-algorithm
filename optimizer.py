import mdarray as md

import pandas as pd
import numpy as np
import sqlite3 as dbs
from quantizer import Quantizer
import quantizer
from discrete_bayes import DiscreteBayes
from pprint import pprint
import random

class Optimizer():
    def __init__(self):
        pass
    
    def create_quantzier(self):
        return Quantizer()
    
    def create_discrete_bayes(self):
        return DiscreteBayes(np.identity(2))
    
    def eval_bounds(self, bounds, nrows=50000, offset=3300000):
        q = self.create_quantzier()
        db = self.create_discrete_bayes()
        bounds
        con = dbs.connect("observations.db")
        counts = q.count_obs(con, bounds, nrows)
        con.close()
        p_dc = q.calc_prob_dc(counts)
        p_d = q.calc_pd(p_dc)
        p_cd = db.calc_prob_cd(p_dc, p_d, [.5, .5])
        drules, e_gains = db.bayes_d_rule(p_cd)
        con = dbs.connect("observations.db")
        test_counts = q.count_obs(con, bounds, nrows, offset)
        cm = db.confusion_matrix(drules, test_counts)
        gain = db.calc_gain(cm, db.gain_matrix)
        return gain
    
    def optimize_bounds(self, start_bounds, rounds=10, d=.05):
        best_ev = 0
        best_bounds = start_bounds
        for i in best_bounds:
            print i
        print '\n'

        for i in range(rounds):
            dim = random.randint(0, len(best_bounds)-2)
            point = random.randint(1, len(best_bounds[dim])-2)
            lowB = best_bounds[dim][point-1]
            bound = best_bounds[dim][point]
            highB = best_bounds[dim][point+1]
            space = highB - lowB
            spacePoints = np.floor(space/d)
            newPoint = random.randint(1, spacePoints) * d + lowB
            best_bounds[dim][point] = newPoint
            test_gain = self.eval_bounds(best_bounds)

            print lowB
            print bound
            print highB
            print newPoint
            print test_gain
            print '\n'