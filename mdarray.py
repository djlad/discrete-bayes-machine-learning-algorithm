from numpy import prod
import operator
import numpy as np

class Mdarray():
    def __init__(self, num_levels):
        '''create virtual multidimensional array
        num_levels -- array with number of values in each component
        '''
        self.num_levels = num_levels
        self.linear_space = [0] * prod(num_levels)
        self.indexes = self.make_md_indexes(num_levels)
    
    def make_md_indexes(self, levels):
        indexes = [[None] for i in range(reduce(operator.mul, levels))]
        cur_val = 0
        for i, level in enumerate(levels):
            for i2, index in enumerate(indexes):
                if len(index) == i:
                    indexes[i2].append(cur_val % level)
                else:
                    indexes[i2][-1] = cur_val % level
                    cur_val += 1
                    if cur_val % level == 0:
                        indexes[i2].append(None)
            cur_val = 0
        if indexes[-1] and indexes[-1][-1] is None:
            indexes[-1].pop()
        return indexes
    
    def total(self):
        return np.sum(self.linear_space)
    
    def __iter__(self):
        return iter(self.indexes)
        #return iter(self.make_md_indexes(self.num_levels))
    
    def __str__(self):
        rep = ""
        indexes = self.make_md_indexes(self.num_levels)
        count = 0
        for i in indexes:
            rep += str(i) + ": " +str(self[i]) + "\n"
            count+=self[i]
        rep += str(count)
        return rep
    
    def __len__(self):
        return len(self.linear_space)
    
    def _get_linear_addr(self, key):
        '''takes tuple of components returns linear address'''
        i = key[0]
        nl_iter = enumerate(self.num_levels)
        next(nl_iter)
        for j, components in nl_iter:
            i = i * components + key[j]
        return i

    def __getitem__(self, key):
        i = self._get_linear_addr(key)
        return self.linear_space[i]

    def __setitem__(self, key, val):
        i = self._get_linear_addr(key)
        self.linear_space[i] = val
