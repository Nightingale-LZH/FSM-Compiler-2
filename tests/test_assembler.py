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


class TestBasicFSMAssembler(unittest.TestCase):
    def test_to_fsm_basic_raw_fsm(self):
        s = "FSM function_name2() { something;    something_else; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_basic_raw_fsm2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_basic_raw_fsm3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 15)
        
    def test_to_fsm_basic_raw_fsm4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 11)
        
    def test_to_fsm_basic_raw_fsm5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 36)
        self.assertEqual(len(fsm.global_variables), 3)
        
        
class TestOptimizedFSMAssemblerLevel1(unittest.TestCase):
    """level 1 opt Test
    
    - optimize consecutive states
    """
    def test_to_fsm_consecutive_opt1(self):
        s = "FSM function_name2() { something;    something_else; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_consecutive_opt2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_consecutive_opt3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 8)
        
    def test_to_fsm_consecutive_opt4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_consecutive_opt5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 20)
        self.assertEqual(len(fsm.global_variables), 3)
        
    def test_to_fsm_consecutive_opt6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_consecutive_opt7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 4)
        
        
class TestOptimizedFSMAssemblerLevel2(unittest.TestCase):
    """level 2 opt Test
    
    - optimize consecutive states
    - optimize chained empty state
    """
    
    def test_to_fsm_consecutive_opt1(self):
        s = "FSM function_name2() { something;    something_else; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_consecutive_opt2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_consecutive_opt3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_consecutive_opt4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_consecutive_opt5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 18)
        self.assertEqual(len(fsm.global_variables), 3)
        
    def test_to_fsm_consecutive_opt6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 4)
        
    def test_to_fsm_consecutive_opt7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)

class TestOptimizedFSMAssemblerLevel3(unittest.TestCase):
    """level 3 opt Test
    
    - optimize consecutive states
    - optimize chained empty state
    - optimize chained branching
    """
    
    def test_to_fsm_opt1(self):
        s = "FSM function_name2() { something;    something_else; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm__opt2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_opt3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_opt4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
    def test_to_fsm_opt5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 16)
        self.assertEqual(len(fsm.global_variables), 3)
        
    def test_to_fsm_opt6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 4)
        
    def test_to_fsm_opt7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        
    def test_to_fsm_opt8(self):
        s = "FSM function_name2() { WHILE(a == 0) { print(\"Doing Things\"); } IF (a==1) {print(\"doing something\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
        
class TestOptimizedFSMAssemblerLevel4(unittest.TestCase):
    """level 3 opt Test
    
    - optimize consecutive states
    - optimize chained empty state
    - optimize chained branching
    - optimize chained merging
    """
    
    def test_to_fsm_opt1(self):
        s = "FSM function_name2() { something;    something_else; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm__opt2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_opt3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_opt4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_opt5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 14)
        self.assertEqual(len(fsm.global_variables), 3)
        
    def test_to_fsm_opt6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        
    def test_to_fsm_opt7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_opt8(self):
        s = "FSM function_name2() { WHILE(a == 0) { print(\"Doing Things\"); } IF (a==1) {print(\"doing something\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_opt9(self):        
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
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 17)
        
    def test_to_fsm_opt10(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                } ELSE IF (b == 0) {
                    b--;
                }
            } WHILE(true);
        }
        
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_opt11(self):        
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
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
        
class TestOptimizedFSMAssemblerLevel5(unittest.TestCase):
    """level 5 opt Test
    
    - optimize consecutive states
    - optimize chained empty state
    - optimize chained branching
    - optimize chained merging
    - optimize consecutive optimized states
    """
    
    def test_to_fsm_opt1(self):
        s = "FSM function_name2() { something;    something_else; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm__opt2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_opt3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_opt4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_opt5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 14)
        self.assertEqual(len(fsm.global_variables), 3)
        
    def test_to_fsm_opt6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        
    def test_to_fsm_opt7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_opt8(self):
        s = "FSM function_name2() { WHILE(a == 0) { print(\"Doing Things\"); } IF (a==1) {print(\"doing something\"); } }"
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_opt9(self):        
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
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 17)
        
    def test_to_fsm_opt10(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                } ELSE IF (b == 0) {
                    b--;
                }
            } WHILE(true);
        }
        
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        
    def test_to_fsm_opt11(self):        
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
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_opt12(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                a++;
                BREAK;
            } ELSE IF (a == 1) {
                a++;
                CONTINUE;
            } ELSE IF (a == 2) {
                a++;
                RETURN;
            } ELSE {
                a++;
            }
            a++;
        }
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        assembler.optimize_FSM_consecutive_states(fsm.starting_node)
        assembler.optimize_FSM_chained_empty_state(fsm.starting_node)
        assembler.optimize_FSM_chained_branching(fsm.starting_node)
        assembler.optimize_FSM_chained_merging(fsm.starting_node)
        assembler.optimize_FSM_consecutive_uncollapsible_states(fsm.starting_node)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
        
class TestAssemblerFunctionality(unittest.TestCase):
    def test_check_wait_stmt_0(self):
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
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        self.assertTrue(assembler.check_wait_statement_usage(fsm.starting_node))
        
    def test_check_wait_stmt_1(self):
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                    YIELD; 
                } ELSE IF (b == 0) {
                    b--;
                    WAIT_UNLESS(b != 0);
                }
            } WHILE(true);
        }
        
        """
        res = parser.parse_to_AST(s)
        fsm = res.to_fsm()
        self.assertFalse(assembler.check_wait_statement_usage(fsm.starting_node))

    def test_to_fsm_opt1(self):
        s = "FSM function_name2() { something;    something_else; }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm__opt2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 2)
        
    def test_to_fsm_opt4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 14)
        self.assertEqual(len(fsm.global_variables), 3)        
        self.assertEqual(len(fsm.global_code_block), 1)

        
    def test_to_fsm_opt6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt8(self):
        s = "FSM function_name2() { WHILE(a == 0) { print(\"Doing Things\"); } IF (a==1) {print(\"doing something\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt9(self):        
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
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 17)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt10(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                } ELSE IF (b == 0) {
                    b--;
                }
            } WHILE(true);
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt11(self):        
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
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        self.assertEqual(len(fsm.global_code_block), 1)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt12(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                    BREAK;
                } ELSE IF (b == 0) {
                    b--;
                }
            } WHILE(true);
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt13(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                    BREAK;
                } ELSE IF (b == 0) {
                    b--;
                    CONTINUE;
                }
                print("Here");
            } WHILE(true);
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
    
    def test_to_fsm_opt14(self):        
        s = """
        FSM function_name_opt9() { 
            int a = -10;
            WHILE(true) {
                WHILE(true) {
                    IF(a == 0) {
                        BREAK;
                    } ELSE IF (a == 1) {
                        CONTINUE;
                    } ELSE IF (a == 2) {
                        RETURN;
                    }
                    a++;
                }
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
    def test_to_fsm_opt15(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                BREAK;
            } ELSE IF (a == 1) {
                CONTINUE;
            } ELSE IF (a == 2) {
                RETURN;
            } 
            a++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        
    def test_to_fsm_opt15(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                a++;
                BREAK;
            } ELSE IF (a == 1) {
                a++;
                CONTINUE;
            } ELSE IF (a == 2) {
                a++;
                RETURN;
            } ELSE {
                a++;
            }
            a++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 4)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        
    def test_to_fsm_opt_for_continue_stmt(self):        
        s = """
        FSM function_name_opt9() { 
            FOR(GLOBAL int i = 0; i < 5; i++) {
                IF (i == 1) { CONTINUE; }
                print(i);
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s))
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
    
    
class TestAssemblerFunctionality_LV5OPT(unittest.TestCase):
    def test_to_fsm_opt1(self):
        s = "FSM function_name2() { something;    something_else; }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm__opt2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 2)
        
    def test_to_fsm_opt4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 14)
        self.assertEqual(len(fsm.global_variables), 3)        
        self.assertEqual(len(fsm.global_code_block), 1)

        
    def test_to_fsm_opt6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt8(self):
        s = "FSM function_name2() { WHILE(a == 0) { print(\"Doing Things\"); } IF (a==1) {print(\"doing something\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt9(self):        
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
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 17)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_optxx10(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                } ELSE IF (b == 0) {
                    b--;
                }
            } WHILE(true);
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 5)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt11(self):        
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
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 7)
        self.assertEqual(len(fsm.global_code_block), 1)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt12(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                    BREAK;
                } ELSE IF (b == 0) {
                    b--;
                }
            } WHILE(true);
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_opt13(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                    BREAK;
                } ELSE IF (b == 0) {
                    b--;
                    CONTINUE;
                }
                print("Here");
            } WHILE(true);
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
    
    def test_to_fsm_opt14(self):        
        s = """
        FSM function_name_opt9() { 
            int a = -10;
            WHILE(true) {
                WHILE(true) {
                    IF(a == 0) {
                        BREAK;
                    } ELSE IF (a == 1) {
                        CONTINUE;
                    } ELSE IF (a == 2) {
                        RETURN;
                    }
                    a++;
                }
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
    def test_to_fsm_opt15a(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                BREAK;
            } ELSE IF (a == 1) {
                CONTINUE;
            } ELSE IF (a == 2) {
                RETURN;
            } 
            a++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        
    def test_to_fsm_opt15(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                a1++;
                RETURN;
            } ELSE {
                a2++;
            }  
            a3++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 4)

    def test_to_fsm_opt16(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                a++;
                BREAK;
            } ELSE IF (a == 1) {
                a++;
                CONTINUE;
            } ELSE IF (a == 2) {
                a++;
                RETURN;
            } ELSE {
                a++;
            }
            a++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
        
class TestAssemblerFunctionality_MealyOpt(unittest.TestCase):
    def test_to_fsm_opt1(self):        
        s = """
        FSM function_name_opt1() { 
            FOR(GLOBAL int i = 0; i < 5; i++) {
                print("hello world!");
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        
    def test_to_fsm_opt2(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                a++;
                BREAK;
            } ELSE IF (a == 1) {
                a++;
                CONTINUE;
            } ELSE IF (a == 2) {
                a++;
                RETURN;
            } ELSE {
                a++;
            }
            a++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_opt3(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                BREAK;
            } ELSE IF (a == 1) {
                CONTINUE;
            } ELSE IF (a == 2) {
                RETURN;
            } 
            a++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm_opt4(self):        
        s = """
        FSM function_name_opt9() { 
            IF(a == 0) {
                a1++;
                RETURN;
            } ELSE {
                a2++;
            }  
            a3++;
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        # self.assertEqual(len(set_return), 6)
        
    def test_to_fsm_optxx1(self):
        s = "FSM function_name2() { something;    something_else; }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_to_fsm__optxx2(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_optxx3(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int j = 0; j < 1000; j++ ) { printf(\"Hello, world!\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 4)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 2)
        
    def test_to_fsm_optxx4(self):
        s =  "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_optxx5(self):
        s =  """
        FSM function_name10a() {
            GLOBAL bool finished = false;
            IF(a==1) { 
                print (\"hello, world!\"); 
            } ELSE IF (a==2) {
                print(\"hello, alt world!\"); 
                YIELD; 
                print("Waited");
            } ELSE IF (a==3) {
                print(\"hello, alt world 2!\"); 
                WAIT(1000/2); 
                FOR(GLOBAL int i = 0; i < 1000; i++ ) {
                    FOR(GLOBAL int j = 0; j < i; j++ ) {
                        DO {
                            if (!finished) { a++; while (true) {}}
                        } WHILE (!finished) ;
                    }
                }
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 8)
        self.assertEqual(len(fsm.global_variables), 3)        
        self.assertEqual(len(fsm.global_code_block), 1)

        
    def test_to_fsm_optxx6(self):
        s = "FSM function_name2() { WHILE(true) {something;    something_else; }}"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_optxx7(self):
        s = "FSM function_name2() { DO {something;    something_else; }WHILE(true);}"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_optxx8(self):
        s = "FSM function_name2() { WHILE(a == 0) { print(\"Doing Things\"); } IF (a==1) {print(\"doing something\"); } }"
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_optxx9(self):        
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
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 10)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
    def test_to_fsm_optxx10(self):        
        s = """
        FSM function_name_opt9() { 
            DO {
                IF (a == 0) {
                    b++;
                } ELSE IF (b == 0) {
                    b--;
                }
            } WHILE(true);
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        self.assertEqual(len(fsm.global_code_block), 0)
        self.assertEqual(len(fsm.global_variables), 0)
        
        
class TestAssembler_FORLoopStructualControl(unittest.TestCase):
    """Structural Control statement in the init and update part of the for loop."""
    
    def test_for_loop_1(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; RETURN) {
                print("hello world");
            }
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
    
    def test_for_loop_2(self):
        s = """
        FSM function_name_opt9() { 
            FOR (RETURN; i < 5; i++) {
                print("hello world");
            }
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
        
    def test_for_loop_3(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; BREAK) {
                print("hello world");
            }
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 4)
        
    def test_for_loop_3x(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; i++) {
                IF(i < 3) {
                    CONTINUE;
                } ELSE {
                    print("hello world");
                }
            }
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
    def test_for_loop_4(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; BREAK) {
                print("hello world 1");
                FOR (GLOBAL int j = 1; j < 5; BREAK) {
                    print("hello world 2");
                    FOR (GLOBAL int k = 1; k < 5; RETURN) {
                        print("hello world 3");
                    }
                }
            }
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
    
    def test_for_loop_5(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; BREAK) {
                print("hello world 1");
                FOR (GLOBAL int j = 1; j < 5; BREAK) {
                    print("hello world 2");
                    FOR (GLOBAL int k = 1; k < 5; BREAK) {
                        print("hello world 3");
                    }
                }
            }
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)

    def test_for_loop_5x(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; i++) {
                IF(i < 3) {
                    BREAK;
                } ELSE {
                    print("hello world");
                }
            }
        }
        
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
    def test_for_loop_5x1(self):
        s = """
        FSM function_name_opt9() { 
            FOR (BREAK; i < 5; i++) {
                print("hello world");
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 0)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node, True))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 6)
        
    def test_for_loop_5x2(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; i++) {
                BREAK;
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 0)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 9)
        
    def test_for_loop_6_opt0(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; CONTINUE) {
                print("hello world");
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 0)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 10)
        
    def test_for_loop_6_opt5(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; CONTINUE) {
                print("hello world");
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 5)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 4)
        
    def test_for_loop_6_opt10(self):
        s = """
        FSM function_name_opt9() { 
            FOR (GLOBAL int i = 1; i < 5; CONTINUE) {
                print("hello world");
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 3)
        
    def test_for_loop_7_opt10(self):
        s = """
        FSM function_name_opt9() { 
            FOR (CONTINUE; i < 5; i++) {
                print("hello world");
            }
        }
        """
        fsm = assembler.generate_FSM_from_AST(parser.parse_to_AST(s), 10)
        # print(code_gen.fsm_to_mermaid(fsm.starting_node))
        # print(code_gen.fsm_to_graphviz_dot(fsm.starting_node))
        set_return = assembler.traverse_FSM(fsm.starting_node)
        self.assertEqual(len(set_return), 2)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    # logging.basicConfig(level=logging.WARNING)
    unittest.main()