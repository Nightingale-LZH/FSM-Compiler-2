import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

import logging
logger = logging.getLogger(__name__)

import unittest


import fsm_compiler.parser as parser
import fsm_compiler.assembler as assembler
from fsm_compiler.ast_types import *

class TestASTTypes(unittest.TestCase):
    def test_copy_by_reference(self):
        s = StatementLine(None, "123")
        res = s.to_fsm()
        self.assertEqual(id(res.starting_node), id(res.ending_node))
        self.assertEqual(res.global_variables, [])

if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    # logging.basicConfig(level=logging.WARNING)
    unittest.main()