import mdarray as md
import pandas as pd
import numpy as np
import random

#mdarray.Mdarray()
class DiscreteBayes():
    def __init__(self, gain_matrix):
        self.gain_matrix = gain_matrix
    
    def calc_prob_cd(self, p_dc, p_d, priors):
        '''compute p(c|d) = p(d|c)*p(c)/p(d)'''
        p_cd = md.Mdarray(p_dc.num_levels)
        total = p_d.total()
        for combo in p_cd:#for each possible observation
            if p_dc[combo] > 0:
                p_cd[combo] = p_dc[combo] * priors[combo[-1]] / (p_d[combo[:-1]]/total)
        return p_cd
    
    def bayes_d_rule(self, p_cd):
        '''assign to class where 
        sum 1 to k of e(cj, ck)*p(cj|d) >= sum 1 to k of e(cj, cn)*p(cj|d)
        where n == 1, 2... K
        '''
        d_rules = md.Mdarray(p_cd.num_levels[:-1])
        e_gains = md.Mdarray(p_cd.num_levels[:-1])
        gm = self.gain_matrix
        for combo in d_rules:#for all d in D
            #best_rule = -1#rule with best expected_value  -1 means invalid
            #start with random assignment:
            best_rule = random.randint(0,p_cd.num_levels[-1]-1)
            best_ev = 0#best expected_value

            for assigned in range(p_cd.num_levels[-1]):
                current_ev = 0
                for true in range(p_cd.num_levels[-1]):
                    #sum up e(true, assigned) * p(c | d)
                    current_ev += gm[true][assigned] * p_cd[combo + [true]]
                if current_ev > best_ev:
                    best_rule = assigned
                    best_ev = current_ev
                
            d_rules[combo] = best_rule
            e_gains[combo] = best_ev

        return d_rules, e_gains
    
    def eval_rules(self, d_rules, counts):
        correct = 0
        total = 0
        for combo in counts:
            total += counts[combo]
            assigned = d_rules[combo[:-1]]
            if assigned == combo[-1]:
                correct += counts[combo]
        return correct, total, float(correct)/total
    
    def confusion_matrix(self, drules, test_counts):
        k = test_counts.num_levels[-1]
        confusion = np.zeros([k, k])
        for combo in test_counts:
            assigned = drules[combo[:-1]]
            if assigned == -1:
                continue
            true = combo[-1]
            confusion[true, assigned] += test_counts[combo]
        total = test_counts.total()
        return confusion/float(total)
    
    def calc_gain(self, gain, confusion):
        evs = np.multiply(gain, confusion)
        return np.sum(evs)
        

        
    #def rule_gain(self, p_cd, )