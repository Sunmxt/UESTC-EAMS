#! /usr/bin/env python

import unittest
from os import getcwd

def test():
    loader = unittest.TestLoader()
    return loader.discover(getcwd())

if __name__ == '__main__':
    unittest.main(defaultTest='test', verbosity=2)
    
