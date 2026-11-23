"""
Unified Test Runner for VibeCheck 2.0.
Executes all unit and integration test suites using Python standard unittest.
"""

import unittest
import sys
import os

# Ensure project root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def run_tests() -> bool:
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    print("\n" + "=" * 70)
    print(" 🧪 RUNNING VIBECHECK 2.0 VERIFICATION TEST SUITE")
    print("=" * 70)
    result = runner.run(suite)
    print("=" * 70)
    if result.wasSuccessful():
        print(f" ✅ ALL {result.testsRun} TESTS PASSED SUCCESSFULLY!")
    else:
        print(f" ❌ {len(result.failures)} FAILURES, {len(result.errors)} ERRORS")
    print("=" * 70 + "\n")
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
