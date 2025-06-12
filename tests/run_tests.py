"""
Test runner for the game.
"""
import unittest
import sys
import os

def discover_tests():
    """Discover and run all unit + integration tests."""
    loader = unittest.TestLoader()
    base_dir = os.path.dirname(__file__)

    # Discover both unit and integration folders
    unit_suite = loader.discover(os.path.join(base_dir, 'unit'))
    integration_suite = loader.discover(os.path.join(base_dir, 'integration'))

    # Combine all test suites
    full_suite = unittest.TestSuite([unit_suite, integration_suite])
    return full_suite

def run_all_tests():
    """Run all discovered tests."""
    suite = discover_tests()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 