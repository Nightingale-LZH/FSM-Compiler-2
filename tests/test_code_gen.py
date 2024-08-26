import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

import logging
logger = logging.getLogger(__name__)

import unittest

import fsm_compiler.parser as parser
import fsm_compiler.assembler as assembler
import fsm_compiler.code_gen as code_gen
from fsm_compiler.ast_types import *

class TestParserPrettyPrint(unittest.TestCase):
    def test_code_gen_1(self):
        s = """
        FSM function_name_opt9() { 
            WHILE(a == 0) { 
                print(\"work 0\"); 
            } 
            WHILE(a == 1) {
                print(\"work 1\"); 
                DO {
                    print(\"work 1a\"); 
                } WHILE (b == 0);
            }
            IF (a == 2) {
                print(\"work 2\"); 
            } 
            IF (a == 3) {
                print(\"work 3\"); 
                IF (b == 0) {
                    print(\"work 3a\"); 
                    YIELD; 
                    print(\"work 3b\"); 
                } 
            } ELSE IF (a == 4) {
                print(\"work 4a\"); 
                YIELD; 
                print(\"work 4b\");
            } ELSE IF (a == 5) {
                print(\"work 5a\"); 
                YIELD; 
                print(\"work 5b\");
            } ELSE {
                print(\"Finally\"); 
            } 
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.generate_AST_from_code(s))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        # print(code_gen.generate_code_from_FSM(fsm))
        
    def test_code_gen_2(self):
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                    WAIT(100);
                } ELSE IF (b == 0) {
                    b--;
                    WAIT(200);
                }
            } WHILE(true);
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.generate_AST_from_code(s))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        # print(code_gen.generate_code_from_FSM(fsm))

if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    # logging.basicConfig(level=logging.WARNING)
    unittest.main()