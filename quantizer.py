import mdarray as md
from scipy.stats import entropy
import numpy as np
from copy import deepcopy

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
        '''calculate p(d) using p(d|c)'''
        p_d = md.Mdarray(p_dc.num_levels[:-1])
        for combination in p_dc:
            p_d[combination[:-1]] += p_dc[combination]
        return p_d

    def calc_side_lengths(self, levels):
        '''calculate lengths of each interval'''
        side_lengths = []
        for dimension in levels:
            side_lengths.append([])
            for i, bound in enumerate(dimension):
                if i+1 < len(dimension):
                    side_lengths[-1].append(dimension[i+1] - bound)
                else:
                    side_lengths[-1].append(1 - bound)
        return side_lengths
    
    def calc_volumes(self, levels):
        side_lengths = self.calc_side_lengths(levels)
        num_levels = map(lambda dim:len(dim), side_lengths)
        volumes = md.Mdarray(num_levels)
        for combo in volumes:
            volume = 1
            for dim, interval in enumerate(combo):
                volume *= side_lengths[dim][interval]
            volumes[combo] = volume
        return volumes


    def ksmooth(self, counts, volumes, kstar):
        '''smooths probability estimates
        counts -- counts for each bin
        volumes -- volumes of each bin
        kstar -- fixed count of surrounding bins
        '''
        combo = counts.indexes[5000]
        num_levels = counts.num_levels
        smoothed_counts = md.Mdarray(num_levels)
        alphas = {}
        for c in range(num_levels[-1]):
            #for each class init alpha to 0
            alphas[c] = 0
        for combo in counts:
            smoothed_count = self.calc_smoothed_bin_volume(combo, counts, volumes, kstar)
            smoothed_counts[combo] += smoothed_count
            alphas[combo[-1]] += smoothed_count
        smoothed_p_dc = smoothed_counts
        for combo in smoothed_p_dc:
            smoothed_p_dc[combo] /= alphas[combo[-1]]
        return smoothed_p_dc
        
    
    def calc_smoothed_bin_volume(self, combo, counts, volumes, kstar):
        '''find bm / Vmstar * vm
        combo -- measurment combination eg (1,5,3,2,3,0)
        counts -- counts of all combos
        volumes -- volumes of all combos
        kstar -- total counts needed for bin smoothing
        '''
        #sum of counts of closest bins
        k = 0
        #sum of volumes of closest bins
        volume = 0
        for neighbor in self.closest_bins(combo, counts.num_levels):
            if k > kstar:
                break
            k += counts[neighbor]
            volume += volumes[neighbor]
        if volume > 0:
            smoothed_volume = k * volumes[combo] / volume 
        else:
            smoothed_volume = 0
        return smoothed_volume

    
    def closest_bins(self, orig_combo, num_levels):
        combo = deepcopy(orig_combo)
        yield combo
        for i, feature_interval in enumerate(combo):
            if i == len(combo)-1:
                break
            combo[i] -= 1
            if combo[i] >= 0 and combo[i] < num_levels[i]:
                yield combo
            combo[i]+=2
            if combo[i] >= 0 and combo[i] < num_levels[i]:
                yield combo
            combo[i] -= 1



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
        print de
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