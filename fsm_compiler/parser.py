import pathlib
import logging
logger = logging.getLogger(__name__)

import lark

from .ast_types import *

__CURRENT_FILE_ABSOLUTE_PATH = pathlib.Path(__file__).parent
PATH_LARK_BASIC_PARSER = __CURRENT_FILE_ABSOLUTE_PATH / "lark_basic_parser.lark"
PATH_LARK_EXPERIMENTAL_PARSER = __CURRENT_FILE_ABSOLUTE_PATH / "lark_experimental_parser.lark"

class CHARACTERS():
    OPEN_BRACKETS = ["(", "[", "{"]
    CLOSING_BRACKETS = [")", "]", "}"]

    DOUBLE_QUOTATION_MARK = '"'
    SINGLE_QUOTATION_MARK = "'"

    ESCAPE = "\\"

with open(PATH_LARK_BASIC_PARSER, "r") as f:
    LARK_BASIC_PARSER = lark.Lark(f, start="fsm_func", propagate_positions=True)
    
with open(PATH_LARK_EXPERIMENTAL_PARSER, "r") as f:
    LARK_EXPERIMENTAL_PARSER = lark.Lark(f, start="fsm_func", propagate_positions=True)
    
    
def generate_AST_from_code(input_str:str) -> ParseResult|None:
    """Parse the given code as input string
    
    This is an alias of `parse_to_AST(input_str:str) -> ParseResult|None`

    Parameters
    ----------
    input_str : str
        input C/C++ code starting at the FSM function

    Returns
    -------
    ParseResult|None
        Return ParseResult when parser successfully parsed the input code
        Return None, otherwise. 
    """
    
    return parse_to_AST(input_str)

def parse_to_AST(input_str:str) -> ParseResult|None:
    """Parse the given code as input string

    Parameters
    ----------
    input_str : str
        input C/C++ code starting at the FSM function

    Returns
    -------
    ParseResult|None
        Return ParseResult when parser successfully parsed the input code
        Return None, otherwise. 
    """
    res_tree = parse_lark_ast(input_str)
    
    return parse_fsm_function(input_str, res_tree)
    
def parse_lark_ast(input_str:str) -> lark.Tree|None:
    return LARK_BASIC_PARSER.parse(input_str)
    
def parse_fsm_function(input_str:str, partial_ast:lark.Tree) -> ParseResult|None:
    assert(partial_ast.children[0].type == "WORD")
    func_name = partial_ast.children[0].value
    
    res_statement = parse_statement(input_str, partial_ast.children[1])
    res_statement = [] if res_statement is None else res_statement
    
    return ParseResult(partial_ast, func_name, res_statement)
    
def parse_statement(input_str:str, partial_ast:lark.Tree) -> Statement|None:
    if partial_ast.data == "statement_ordinary":
        return StatementOrdinary(partial_ast, input_str[partial_ast.meta.start_pos : partial_ast.meta.end_pos])
    
    if partial_ast.data == "statement_partial":
        return parse_statement_partial(input_str, partial_ast.children[0])
    
    if partial_ast.data == "statement_block":
        return parse_statement_block(input_str, partial_ast)
    
    if partial_ast.data == "statement_for":
        return parse_statement_for(input_str, partial_ast)
    
    if partial_ast.data == "statement_while":
        return parse_statement_while(input_str, partial_ast)
    
    if partial_ast.data == "statement_do_while":
        return parse_statement_do_while(input_str, partial_ast)
    
    if partial_ast.data == "statement_if" or partial_ast.data == "statement_if_else":
        return parse_statement_if_else(input_str, partial_ast)
    
    
def parse_statement_partial(input_str:str, partial_ast:lark.Tree) -> Statement|None:
    # print(partial_ast.pretty())
    if partial_ast.data == "partialstmt":
        return StatementLine(partial_ast, input_str[partial_ast.meta.start_pos : partial_ast.meta.end_pos])
    
    if partial_ast.data == "partialstmt_declaration":
        return parse_statement_declaration(input_str, partial_ast.children[0])
    
    if partial_ast.data == "partialstmt_yield":
        return StatementWait(partial_ast, "")
    
    if partial_ast.data == "partialstmt_wait":
        expr = partial_ast.children[0]
        return StatementWait(partial_ast, input_str[expr.meta.start_pos : expr.meta.end_pos])
    
    if partial_ast.data == "partialstmt_wait_until":
        condition = partial_ast.children[0]
        return StatementWaitUnless(partial_ast, input_str[condition.meta.start_pos : condition.meta.end_pos])
  
  
def parse_statement_if_else(input_str:str, partial_ast:lark.Tree) -> Statement|None:
    if partial_ast.data == "statement_if":
        condition, statement = partial_ast.children
        return StatementIf(
            partial_ast,
            [
                IfCase(
                    input_str[condition.meta.start_pos : condition.meta.end_pos],
                    parse_statement(input_str, statement)
                )
            ]
        )
        
    elif partial_ast.data == "statement_if_else":
        condition, statement, else_statement = partial_ast.children
        return StatementIf(
            partial_ast, 
            [
                IfCase(
                    input_str[condition.meta.start_pos : condition.meta.end_pos],
                    parse_statement(input_str, statement)
                ),
                IfCase(
                    "",
                    parse_statement(input_str, else_statement)
                )
            ]
        )
    
def parse_statement_for(input_str:str, partial_ast:lark.Tree) -> Statement|None:
    initialization, condition, update, statement = partial_ast.children
    
    return StatementFor(
        partial_ast,
        parse_statement_partial(input_str, initialization),
        input_str[condition.meta.start_pos : condition.meta.end_pos],
        parse_statement_partial(input_str, update),
        parse_statement(input_str, statement)
    )
    
def parse_statement_while(input_str:str, partial_ast:lark.Tree) -> Statement|None:
    condition, statement = partial_ast.children
    
    return StatementWhile(
        partial_ast,
        input_str[condition.meta.start_pos : condition.meta.end_pos],
        parse_statement(input_str, statement)
    )
    
def parse_statement_do_while(input_str:str, partial_ast:lark.Tree) -> Statement|None:
    statement, condition = partial_ast.children
    
    return StatementDoWhile(
        partial_ast,
        input_str[condition.meta.start_pos : condition.meta.end_pos],
        parse_statement(input_str, statement)
    )
    
def parse_statement_block(input_str:str, partial_ast:lark.Tree) -> StatementLine|None:
    statements = partial_ast.children
    
    ret_val = []
    
    for statement in statements:
        ret_stmt = parse_statement(input_str, statement)
        if ret_stmt is not None:
            ret_val.append(ret_stmt)
        else:
            # something wrong
            pass
        
    return StatementBlock(partial_ast, ret_val)

def parse_statement_declaration(input_str:str, partial_ast:lark.Tree) -> StatementDeclaration|None:
    if partial_ast.data == "declaration":
        return StatementLine(
            partial_ast,
            input_str[partial_ast.meta.start_pos : partial_ast.meta.end_pos]
        )
        
    elif partial_ast.data == "declaration_global":
        datatype, variable = partial_ast.children
        return StatementDeclaration(
            partial_ast,
            input_str[datatype.meta.start_pos : datatype.meta.end_pos],
            input_str[variable.meta.start_pos : variable.meta.end_pos],
            True
        )
    
    elif partial_ast.data == "declaration_initialization":
        return StatementLine(
            partial_ast,
            input_str[partial_ast.meta.start_pos : partial_ast.meta.end_pos]
        )
        
    elif partial_ast.data == "declaration_initialization_global":
        datatype, variable, expression = partial_ast.children
        return StatementDeclarationInit(
            partial_ast,
            input_str[datatype.meta.start_pos : datatype.meta.end_pos],
            input_str[variable.meta.start_pos : variable.meta.end_pos],
            input_str[expression.meta.start_pos : expression.meta.end_pos],
            True
        )
        
    elif partial_ast.data == "declaration_class_init":
        return StatementLine(
            partial_ast,
            input_str[partial_ast.meta.start_pos : partial_ast.meta.end_pos]
        )
        