import sys
import os
import unittest

# Add src to sys.path
sys.path.insert(0, os.path.abspath('src'))

# Load tests
loader = unittest.TestLoader()
suite = loader.discover('tests')

# Run tests
runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
result = runner.run(suite)

if not result.wasSuccessful():
    sys.exit(1)
