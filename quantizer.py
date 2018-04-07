import mdarray as md
from scipy.stats import entropy
import numpy as np

class Quantizer():
    def __init__(self, levels=None):
        self.levels = levels

    def count_obs(self, con, levels=None, nrows=1000, offset=0):
        ''' count frequency of each possible tuple
            example: levels = [equal_spaced_bounds(3) for i in range(5)]
        '''
        if not levels:
            levels = self.levels
        counts = md.Mdarray(map(lambda e:len(e),levels))
        quantizers = map(gen_quantize, levels)

        c = con.cursor()
        query = '''
        SELECT f1,f2,f3,f4,f5,class
        FROM observations limit {} offset {}
        '''.format(nrows, offset)
        c.execute(query)
        for i in range(nrows):
            obs = c.fetchone()
            mdAddress = map(lambda obs:quantizers[obs[0]](obs[1]),
                            enumerate(obs))
            counts[mdAddress] += 1
        con.close()
        return counts

    def calc_prob_dc(self, observation_counts):
        '''calc p(d|c) using count_obs output
        observation_counts -- hashmap where 
        observation_counts[(f1, f2, ..., class)] gives count of observations
        '''
        totals = {}
        total_observations = 0.0
        classes = observation_counts.num_levels[-1]
        p_dc = md.Mdarray(observation_counts.num_levels)
        for i in range(classes):
            totals[i] = 0
        for combination in observation_counts:
            totals[combination[-1]] += observation_counts[combination]
            total_observations += observation_counts[combination]
        for combination in observation_counts:
            c = combination[-1]
            if observation_counts[combination] > 0:
                #p_d = observation_counts[combination]/total_observations
                #observation_counts[combination] /= float(totals[c]) * p_d
                #if combination == [0,0,0,0,0,1] or combination == [0,0,0,0,0,0]:
                #    print p_d
                p_dc[combination] = observation_counts[combination] / float(totals[c])
        return p_dc
    
    def calc_pd(self, p_dc):
        p_d = md.Mdarray(p_dc.num_levels[:-1])
        for combination in p_dc:
            p_d[combination[:-1]] += p_dc[combination]
        return p_d

    def dimensional_probabilities(self, df, num_intervals=10000):
        quantize = gen_quantize(equal_spaced_bounds(num_intervals))
        df = df.applymap(lambda e: quantize(e))
        def get_probability(col_name):
            return df[col_name].value_counts()/len(df)
        return map(get_probability, df.columns)
    
    def dimensional_entropy(self, dim_probabilities):
        '''takes dimensional probabilities returns entropy'''
        return map(lambda dim: entropy(dim, None, 2), dim_probabilities)
    
    def calc_levels(self, dimensional_entropy, total_bins=10000):
        '''takes entropy of each dimension and returns
        array of levels of each dimension. distributes 
        bins according to each level according to its entropy
        '''
        de = dimensional_entropy
        entropy_sum = sum(dimensional_entropy)
        entropy_proportions = map(lambda entropy: entropy/entropy_sum,
                                  dimensional_entropy)
        exact_dim_bins = np.power(total_bins, entropy_proportions)
        dim_bins = np.ceil(exact_dim_bins)
        return dim_bins
    
    def levels_from_data(self, df):
        dp = self.dimensional_probabilities(df,10000)
        de = self.dimensional_entropy(dp[:-1])
        return self.calc_levels(de, 10000)
        
    def data_to_hash_count(self, con):
        '''iterates through data and creates a dict with values'''
        cursor = con.cursor()
        cursor.execute('select * from observations')
        frequency = {}
        for i in range(10000):
            obs = cursor.fetchone()
            if obs in frequency:
                frequency[obs]+=1
            else:
                frequency[obs] = 1
        con.close()
        return frequency
        
        
    

def equal_discrete_func(x, levels=3):
    ratio = x * levels
    return int(np.floor(ratio))

def equal_spaced_bounds(num_bounds, max=1):
    return [i*max/float(num_bounds) for i in range(num_bounds)]

def gen_quantize(bounds):
    def quantize(val):
        low = 0
        high = len(bounds)
        mid = (low+high)/2
        while not low == high:
            if val > bounds[mid]:
                low = mid
            elif val < bounds[mid]:
                high = mid
            elif val == bounds[mid]:
                return mid
            mid = (low+high)/2
            if low+1 == high:
                return low
    return quantize