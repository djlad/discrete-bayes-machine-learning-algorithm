import unittest
import math
import pandas as pd
import numpy as np
import discrete_bayes as dbayes
import sqlite3 as db

class TestDiscreteBayes(unittest.TestCase):
    def test_equal_discretize(self):
        '''column_names = ["f1","f2","f3","f4","f5","class"]
        #column_names = None
        data = pd.read_csv("pr_data", names=column_names, delimiter='\s+', nrows=1000)
        '''
        con = db.connect("observations.db")
        data = pd.read_sql("select count(f1) from observations group by f1,f2,f3,f4,f5 limit 1", con)
        con.close()
        print data
        '''
        data = data.drop(["class"], axis=1)
        print data
        data = data.apply(equal_discrete_func)
        print "stuff"
        d = data.groupby(column_names[:-1]).count()
        for i in d:
            print i
            '''

def equal_discrete_func(x, levels=3):
    ratio = x * levels
    return np.floor(ratio)

if __name__ == "__main__":
    unittest.main()

