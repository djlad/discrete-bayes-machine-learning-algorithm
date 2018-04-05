import mdarray
import pandas as pd

#mdarray.Mdarray()
class DiscreteBayes():
    def __init__(self, gain_matrix):
        self.gain_matrix = gain_matrix
    
    def calc_prob_cd(self, prob_dc, priors):
        '''compute p(c|d)'''
        pass
