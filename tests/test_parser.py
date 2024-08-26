import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

import logging
logger = logging.getLogger(__name__)

import unittest

import fsm_compiler.parser as parser
import fsm_compiler.ast_types as ast_types


class TestParserBasic(unittest.TestCase):
    
    def test_parser_basic(self):
        s = "FSM function_name1() {}"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name1")
        self.assertEqual(res.statements.lines, [])
        
    def test_parser_single_statement(self):
        s = "FSM function_name2() { something;    something_else; }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name2")
        self.assertEqual(res.statements.lines[0].block, "something")
        self.assertEqual(res.statements.lines[1].block, "something_else")
        
    def test_parser_declaration_and_string(self):
        s = "FSM function_name3() { str something.this = \";\" ; regular.statement = \"regular\\\" escaped \\\"\"; }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name3")
        self.assertEqual(res.statements.lines[0].block, "str something.this = \";\"")
        self.assertEqual(res.statements.lines[1].block, "regular.statement = \"regular\\\" escaped \\\"\"")
        
    def test_parser_name_scope(self):
        s = "FSM function_name4() { std::string hello.world = 2; std::printf(\"hello\"); }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name4")
        self.assertEqual(res.statements.lines[0].block, "std::string hello.world = 2")
        self.assertEqual(res.statements.lines[1].block, "std::printf(\"hello\")")
        
    def test_parser_declaration(self):
        s = "FSM function_name5() { std::vector a(0, 0); GLOBAL float f; int i = 5+5; int j; GLOBAL std::string s = \"123\"; unsigned int x=0; }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name5")
        self.assertEqual(res.statements.lines[0].block, "std::vector a(0, 0)")

        line1: parser.StatementDeclaration = res.statements.lines[1]
        self.assertEqual(line1.datatype, "float")
        self.assertEqual(line1.variable, "f")
        self.assertTrue(line1.make_global)
        
        self.assertEqual(res.statements.lines[2].block, "int i = 5+5")
        self.assertEqual(res.statements.lines[3].block, "int j")

        line4:parser.StatementDeclarationInit = res.statements.lines[4]
        self.assertEqual(line4.datatype, "std::string")
        self.assertEqual(line4.variable, "s")
        self.assertEqual(line4.expression, "\"123\"")
        self.assertTrue(line4.make_global)
        
        self.assertEqual(res.statements.lines[5].block, "unsigned int x=0")
        
        
    def test_parser_for_loop(self):
        s = "FSM function_name6() { FOR(GLOBAL int i = 0; i < 1000; i++ ) FOR(GLOBAL int i = 0; i < 1000; i++ ) { printf(\"Hello, world!\"); } }"
        res = parser.parse_to_AST(s)

        self.assertEqual(res.function_name, "function_name6")
        
        forloop1: parser.StatementFor = res.statements.lines[0]
        assign1: parser.StatementDeclarationInit = forloop1.initialization
        
        self.assertEqual(assign1.datatype, "int")
        self.assertEqual(assign1.variable, "i")
        self.assertEqual(assign1.expression, "0")
        self.assertTrue(assign1.make_global)
        
        self.assertEqual(forloop1.condition, "i < 1000")
        
        update1: parser.StatementLine = forloop1.update
        self.assertEqual(update1.block, "i++")
        
        forloop2: parser.StatementFor = forloop1.statements
        
        assign2: parser.StatementDeclarationInit = forloop2.initialization
        
        self.assertEqual(assign2.datatype, "int")
        self.assertEqual(assign2.variable, "i")
        self.assertEqual(assign2.expression, "0")
        self.assertTrue(assign2.make_global)
        
        self.assertEqual(forloop2.condition, "i < 1000")
        
        update2: parser.StatementLine = forloop2.update
        self.assertEqual(update2.block, "i++")
        
        stmt_block: parser.StatementBlock = forloop2.statements
        self.assertEqual(stmt_block.lines[0].block, "printf(\"Hello, world!\")")
        
    
    def test_parser_while_loop(self):
        s = "FSM function_name7() { WHILE(true) {WHILE(false) {}} }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name7")
        
        while1: parser.StatementWhile = res.statements.lines[0]
        self.assertEqual(while1.condition, "true")
        
        while2: parser.StatementWhile = while1.statements.lines[0]
        self.assertEqual(while2.condition, "false")
        
        stmtblock: parser.StatementBlock = while2.statements
        self.assertEqual(stmtblock.lines, [])
    
    
    def test_parser_do_while_loop(self):
        s = "FSM function_name8() { DO{WHILE(false) {}} WHILE(true); }"
        res = parser.parse_to_AST(s)
    
        self.assertEqual(res.function_name, "function_name8")
        
        while1: parser.StatementDoWhile = res.statements.lines[0]
        self.assertEqual(while1.condition, "true")
        
        while2: parser.StatementWhile = while1.statements.lines[0]
        self.assertEqual(while2.condition, "false")
        
        stmtblock: parser.StatementBlock = while2.statements
        self.assertEqual(stmtblock.lines, [])
    
    
    def test_parser_if(self):
        s = "FSM function_name9() { IF(a==1) { print (\"hello, world!\"); } }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name9")
        
        if1: parser.StatementIf = res.statements.lines[0]
        self.assertEqual(if1.cases[0].condition, "a==1")
        self.assertEqual(if1.cases[0].statements.lines[0].block, "print (\"hello, world!\")")
        
    
    def test_parser_if_else(self):
        s = "FSM function_name10() { IF(a==1) { print (\"hello, world!\"); } ELSE { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)

        self.assertEqual(res.function_name, "function_name10")
        
        if1: parser.StatementIf = res.statements.lines[0]
        self.assertEqual(if1.cases[0].condition, "a==1")
        self.assertEqual(if1.cases[0].statements.lines[0].block, "print (\"hello, world!\")")
        self.assertEqual(if1.cases[1].condition, "")
        self.assertEqual(if1.cases[1].statements.lines[0].block, "print(\"hello, alt world!\")")
       
       
    def test_parser_if_else_chained(self):
        s = "FSM function_name10a() { IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); } }"
        res = parser.parse_to_AST(s)

        self.assertEqual(res.function_name, "function_name10a")
        
        if1: parser.StatementIf = res.statements.lines[0]
        self.assertEqual(len(if1.cases), 2)
        self.assertEqual(if1.cases[0].condition, "a==1")
        self.assertEqual(if1.cases[0].statements.lines[0].block, "print (\"hello, world!\")")
        self.assertEqual(if1.cases[1].condition, "")
        
        if2: parser.StatementIf = if1.cases[1].statements
        self.assertEqual(len(if2.cases), 1)
        self.assertEqual(if2.cases[0].condition, "a==2")
        self.assertEqual(if2.cases[0].statements.lines[0].block, "print(\"hello, alt world!\")")
        
    def test_parser_if_else_2(self):
        s = "FSM function_name10a() { cin >> n; IF(a==1) print (\"hello, world!\"); ELSE print(\"hello, alt world!\"); }"
        res = parser.parse_to_AST(s)

        self.assertEqual(res.function_name, "function_name10a")
        
        if1: parser.StatementIf = res.statements.lines[1]
        self.assertEqual(len(if1.cases), 2)
        self.assertEqual(if1.cases[0].condition, "a==1")
        self.assertEqual(if1.cases[0].statements.block, "print (\"hello, world!\")")
        self.assertEqual(if1.cases[1].condition, "")
        self.assertEqual(if1.cases[1].statements.block, "print(\"hello, alt world!\")")

        
    def test_parser_if_else_chained_3(self):
        s = "FSM function_name10a() { cin >> n; IF(a==1) { print (\"hello, world!\"); } ELSE IF (a==2) { print(\"hello, alt world!\"); }  }"
        res = parser.parse_to_AST(s)

        self.assertEqual(res.function_name, "function_name10a")
        
        if1: parser.StatementIf = res.statements.lines[1]
        self.assertEqual(len(if1.cases), 2)
        self.assertEqual(if1.cases[0].condition, "a==1")
        self.assertEqual(if1.cases[0].statements.lines[0].block, "print (\"hello, world!\")")
        self.assertEqual(if1.cases[1].condition, "")
        
        if2: parser.StatementIf = if1.cases[1].statements
        self.assertEqual(len(if2.cases), 1)
        self.assertEqual(if2.cases[0].condition, "a==2")
        self.assertEqual(if2.cases[0].statements.lines[0].block, "print(\"hello, alt world!\")")
        
    def test_parser_yield_wait_waitunless(self):
        s = "FSM function_name11() { YIELD; WAIT(1000/2); WAIT_UNLESS(false); }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name11")
        
        wait0: parser.StatementWait = res.statements.lines[0]
        self.assertEqual(wait0.wait_time_ms, "")
        
        wait1: parser.StatementWait = res.statements.lines[1]
        self.assertEqual(wait1.wait_time_ms, "1000/2")
        
        wait_unless: parser.StatementWaitUnless = res.statements.lines[2]
        self.assertEqual(wait_unless.condition, "false")
        
        
    def test_parser_cpp_test_code(self):
        s = """
        FSM func_cpp_test_code() {
            int n;

            cout << "Enter an integer: ";
            cin >> n;

            if ( n % 2 == 0)
                cout << n << " is even.";
            else
                cout << n << " is odd.";
                

            int n;
            int sum = 0;

            cout << "Enter a positive integer: ";
            cin >> n;

            for (int i = 1; i <= n; ++i) {
                sum += i;
            }

            cout << "Sum = " << sum;
            return 0;
        }
        """
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "func_cpp_test_code")
        self.assertEqual(len(res.statements.lines), 11)
    
    def test_parser_cpp_test_code1(self):
        s = """
        FSM func_cpp_test_code() {
            cin >> n; IF ( n % 2 == 0) cout << n << " is even."; ELSE cout << n << " is odd.";
        }
        """
        res = parser.parse_to_AST(s)
        self.assertEqual(len(res.statements.lines), 2)
        
    def test_parser_cpp_comment(self):
        s = """
        FSM func_cpp_test_code() {
            int n;

            //  some comment
            cout << "Enter an integer: ";
            cin >> n;

            if ( n % 2 == 0)
                cout << n << " is even."; //another comment
            else
                cout << n << " is odd.";
                
            // TODO
            int n;
            int sum = 0;

            cout << "Enter a positive integer: ";
            cin >> n;

            for (int i = 1; i <= n; ++i) {
                sum += i; // adding things together
            }

            cout << "Sum = " << sum;
            return 0;   //  safe exit
        }
        """
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "func_cpp_test_code")
        self.assertEqual(len(res.statements.lines), 11)
        
    def test_parser_break_continue_return(self):
        s = "FSM function_name_cbr() { BREAK; CONTINUE; RETURN; }"
        res = parser.parse_to_AST(s)
        
        self.assertEqual(res.function_name, "function_name_cbr")
        self.assertIsInstance(res.statements.lines[0], ast_types.StatementBreak)
        self.assertIsInstance(res.statements.lines[1], ast_types.StatementContinue)
        self.assertIsInstance(res.statements.lines[2], ast_types.StatementReturn)
    

class TestParserPrettyPrint(unittest.TestCase):
    
    def test_print_parser_declaration(self):
        s = """
        FSM function_name_print_0() { 
            std::vector a(0, 0); 
            GLOBAL float f; 
            int i = 5+5; 
            int j; 
            GLOBAL std::string s = \"123\"; 
            unsigned int x=0; 
            IF ( n % 2 == 0) cout << n << " is even."; ELSE cout << n << " is odd.";
        }
        """
        res = parser.parse_to_AST(s)
        
        # print(res.print_pretty())

if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    # logging.basicConfig(level=logging.WARNING)
    unittest.main()