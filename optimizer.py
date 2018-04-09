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
    
    def eval_bounds(self, bounds, nrows=1000000, offset=3300000, trainoffset=0, kstar=0):
        q = self.create_quantzier()
        db = self.create_discrete_bayes()
        bounds
        con = dbs.connect("observations.db")
        counts = q.count_obs(con, bounds, nrows, trainoffset)
        con.close()

        if kstar > 0:
            print 'ksmooth'
            volumes = q.calc_volumes(bounds)
            #k smoothed probabilities
            p_dc = q.ksmooth(counts, volumes, 223)
        else:
            #MLE probabilities
            p_dc = q.calc_prob_dc(counts)
        p_d = q.calc_pd(p_dc)
        p_cd = db.calc_prob_cd(p_dc, p_d, [.5, .5])
        drules, e_gains = db.bayes_d_rule(p_cd)
        con = dbs.connect("observations.db")
        test_counts = q.count_obs(con, bounds, nrows, offset)
        cm = db.confusion_matrix(drules, test_counts)
        gain = db.calc_gain(cm, db.gain_matrix)
        return gain
    
    def optimize_bounds(self, start_bounds, rounds=1000000, d=.01):
        nrows = 50000
        offset = 3300000
        trainoffset = 0

        best_gain = 0
        best_bounds = start_bounds
        #number of rounds since change:
        no_change_rounds = 0
        for i in best_bounds:
            print i
        print '\n'
        
        for i in range(rounds):
            dim = random.randint(0, len(best_bounds)-2)
            point = random.randint(1, len(best_bounds[dim])-1)
            lowB = best_bounds[dim][point-1]
            bound = best_bounds[dim][point]
            if point == len(best_bounds[dim])-1:
                highB = 1
            else:
                highB = best_bounds[dim][point+1]
            space = highB - lowB
            spacePoints = np.floor(space/d)
            if spacePoints > 1:
                newBound = random.randint(1, spacePoints) * d + lowB
                best_bounds[dim][point] = newBound
                test_gain = self.eval_bounds(best_bounds, nrows)

                if test_gain >= best_gain :
                    best_gain = test_gain
                    no_change_rounds = 1
                else:
                    best_bounds[dim][point] = bound
                    no_change_rounds += 1
            
                if no_change_rounds%10 == 0:
                    #switch up data if no change
                    print "changed training set"
                    trainoffset = (trainoffset+nrows) % offset
                    print trainoffset
                print no_change_rounds
                print test_gain
                print best_gain
                print best_bounds
                print '\n'