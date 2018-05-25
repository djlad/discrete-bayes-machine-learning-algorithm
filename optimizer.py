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

import sys, os
from pprint import pprint

class Optimizer():
    def __init__(self):
        pass
    
    def create_quantzier(self):
        return Quantizer()
    
    def create_discrete_bayes(self):
        return DiscreteBayes(np.identity(2))
    
    def eval_bounds(self, bounds, config):
        nrows = config['nrows']
        offset = config['offset']
        trainoffset = config['trainoffset']
        kstar = config['kstar']
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
    
    def optimize_bounds(self, config, write_output):
        print config
        time_start = time.time()
        rounds = config['rounds']
        d = config['d']
        seed = config['seed']
        #number of rows to use at a time
        nrows = config['nrows']#number of training observations to use at a time
        offset = config['offset']#beginning of testing data
        trainoffset = config['trainoffset']#beginning of training data
        best_bounds = config['start_bounds']
        best_gain = test_gain = self.eval_bounds(best_bounds, config)

        #number of rounds since change:
        #show current bounds:
        for i in best_bounds:
            print i
        print '\n'

        '''record initial evaluation'''
        no_change_rounds = 0
        round_results = {
                    'input file: {}': config['input file'],
                    'total time: {}': time.time()-time_start,
                    'rounds since change: {}': no_change_rounds,
                    'best gain: {}': best_gain,
                    'best bounds: {}': best_bounds
                    }
        result_str = self.create_round_res_str(round_results)
        write_output(result_str)
        print result_str + '\n'

        random.seed(seed)
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
                test_gain = self.eval_bounds(best_bounds, config)

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
                            'input file: {}': config['input file'],
                            'total time: {}': time.time()-time_start,
                            'rounds since change: {}': no_change_rounds,
                            'test gain: {}': test_gain,
                            'best gain: {}': best_gain,
                            'best bounds: {}': best_bounds
                         }

                result_str = self.create_round_res_str(round_results)
                write_output(result_str)
                print result_str
                print '\n'
    
    def create_round_res_str(self, round_results):
        '''creates results string for one iteration'''
        formatted_strs = []
        for result in round_results:
            formatted_str = result.format(round_results[result])
            formatted_strs.append(formatted_str)
        result_str = '\n'.join(formatted_strs)
        return result_str




def read_input(file_name):
    f = open(os.path.join('inputs', file_name), 'r')
    txt = f.read()
    f.close()
    return txt

def gen_write_output(input_file_name):
    '''function for writing result'''
    output_file_name = input_file_name.replace('.txt', '')
    output_file_name += '-output.txt'
    def write_output(result_str):
        f = open(os.path.join('outputs', output_file_name), 'w')
        txt = f.write(result_str)
        f.close()
        return txt
    return write_output
    

def run_optimize_bounds(file_name):
    op = Optimizer()
    ctext = read_input(file_name)
    config = eval(ctext)
    config['input file'] = file_name
    write_output_function = gen_write_output(file_name)
    op.optimize_bounds(config, write_output_function)

if __name__ == '__main__':
    input_file = sys.argv[1]
    run_optimize_bounds(input_file)
    