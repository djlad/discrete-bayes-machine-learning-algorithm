import mdarray as md

import pandas as pd
import numpy as np
import sqlite3 as dbs
from quantizer import Quantizer
import quantizer
from discrete_bayes import DiscreteBayes
from pprint import pprint
import random
import time

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
        con = dbs.connect("observations.db")
        counts = q.count_obs(con, bounds, nrows, trainoffset)
        con.close()

        if kstar > 0:
            print 'ksmooth'
            volumes = q.calc_volumes(bounds)
            #k smoothed probabilities
            p_dc = q.ksmooth(counts, volumes, kstar)
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
    
    def optimize_bounds(self, config):
        print config
        '''
        rounds = 1000000
        d = .01
        time_start = time.time()
        seed = 849323344
        #number of rows to use at a time
        nrows = 50000#number of training observations to use at a time
        offset = 3300000#beginning of testing data
        trainoffset = 0#beginning of training data
        best_gain = 0
        best_bounds = config['start_bounds']
        #number of rounds since change:
        no_change_rounds = 0
        kstar = 0
        '''
        time_start = time.time()
        rounds = 1000000
        d = config['d']
        seed = config['seed']
        #number of rows to use at a time
        nrows = config['nrows']#number of training observations to use at a time
        offset = config['offset']#beginning of testing data
        trainoffset = config['trainoffset']#beginning of training data
        best_gain = config['best_gain']
        best_bounds = config['start_bounds']
        kstar = config['kstar']
        #number of rounds since change:
        no_change_rounds = 0
        print 'kstar'
        print kstar


        random.seed(seed)

        #show current bounds:
        for i in best_bounds:
            print i
        print '\n'
        
        for i in range(rounds):
            #choose random dimension and boundary
            dim = random.randint(0, len(best_bounds)-2)
            point = random.randint(1, len(best_bounds[dim])-1)
            #get left boundary
            lowB = best_bounds[dim][point-1]
            #get boundary
            bound = best_bounds[dim][point]
            #get right boundary
            if point == len(best_bounds[dim])-1:
                highB = 1
            else:
                highB = best_bounds[dim][point+1]
            #find points between previous and next boundary:
            space = highB - lowB
            spacePoints = np.floor(space/d)-1
            if spacePoints > 1:
                #pick random point between previous and next boundary
                newBound = random.randint(1, spacePoints) * d + lowB
                best_bounds[dim][point] = newBound
                #test new boundary
                test_gain = self.eval_bounds(best_bounds, nrows, offset, trainoffset, kstar)

                #update boundary
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
                
                round_results = {
                            'total time: {}': time.time()-time_start,
                            'rounds since change: {}': no_change_rounds,
                            'test gain: {}': test_gain,
                            'best gain: {}': best_gain,
                            'best bounds: {}': best_bounds
                         }

                result_str = self.create_round_res_str(round_results)
                print result_str
                print '\n'
    
    def create_round_res_str(self, round_results):
            formatted_strs = []
            for result in round_results:
                formatted_str = result.format(round_results[result])
                formatted_strs.append(formatted_str)
            result_str = '\n'.join(formatted_strs)
            return result_str