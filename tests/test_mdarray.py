import unittest
import mdarray as md
import operator
from pprint import pprint

class TestMdarray(unittest.TestCase):

    def test_set_md_array_elements(self):
        test_levels = [3,4,5,6]
        m = md.Mdarray(test_levels)
        indexes = m.make_md_indexes(test_levels)
        for i, index in enumerate(indexes):
            m[index] = i
        for i, index in enumerate(indexes):
            self.assertEqual(i, m[index])
        

if __name__ == "__main__":
    unittest.main()