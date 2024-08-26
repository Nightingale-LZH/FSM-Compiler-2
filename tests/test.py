import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

import logging
logger = logging.getLogger(__name__)

import unittest

import test_parser
import test_assembler
import test_ast_types
import test_code_gen

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # add tests to the test suite
    suite.addTests(loader.loadTestsFromModule(test_parser))
    suite.addTests(loader.loadTestsFromModule(test_assembler))
    suite.addTests(loader.loadTestsFromModule(test_ast_types))
    suite.addTests(loader.loadTestsFromModule(test_code_gen))

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)