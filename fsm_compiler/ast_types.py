import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass

import lark

from . import code_template
    
PRETTY_PRINT_INDENTATION_WIDTH = 2

def __get_indentation(indentation:int) -> str:
    return " " * (PRETTY_PRINT_INDENTATION_WIDTH * indentation)

# -------------------------------------------------- #
#                Finite State Machine                #
# -------------------------------------------------- #

class FSMTransition:    # forward declaration
    pass

@dataclass
class FSMNode():
    """if `entry_condition` is "", then it will never prevent from entry"""
    code_block: list[str]
    transitions: list[FSMTransition]
    collapsible: bool = True # invariant: if this node is pointed by multiple nodes, then this one is not collapsible
    entry_condition: str = ""
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, value: object) -> bool:
        return id(self) == id(value)

@dataclass
class FSMTransition:
    """if `condition` is "", then it will always transition"""
    code_block: list[str]
    condition: str
    target_node: FSMNode
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, value: object) -> bool:
        return id(self) == id(value)

@dataclass
class FSMGlobalVar:
    var_type: str
    var_name: str

@dataclass
class FSMMachine:
    global_variables: list[FSMGlobalVar]
    global_code_block: list[str]
    starting_node: FSMNode
    fsm_name: str

@dataclass
class TO_FSM_Return:
    starting_node: FSMNode
    ending_node: FSMNode
    global_variables: list[FSMGlobalVar]
    
    return_nodes: list[FSMNode]
    break_nodes: list[FSMNode]
    continue_nodes: list[FSMNode]

# -------------------------------------------------- #
#                        AST                         #
# -------------------------------------------------- #

@dataclass
class Statement():
    lark_ast: lark.Tree
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        return None
    
    def print_pretty(self, indentation:int=0) -> str:
        pass

@dataclass
class StatementLine(Statement):
    block: str
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node = FSMNode(["{};".format(self.block)], [])
        return TO_FSM_Return(node, node, [], [], [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
@dataclass
class StatementOrdinary(Statement):
    block: str
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node = FSMNode([self.block], [])
        return TO_FSM_Return(node, node, [], [], [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
@dataclass
class StatementBlock(Statement):
    lines: list[Statement]
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node_start = FSMNode([], [])
        ret_global_vars = []
        
        ret_return_nodes = []
        ret_break_nodes = []
        ret_continue_nodes = []
        
        node_end = node_start
        for line in self.lines:
            fsm_return_statement = line.to_fsm(fsm_name)
            
            # for gv in fsm_return_statement.global_variables:
            #     ret_global_vars.append(gv)
                
            ret_global_vars    += fsm_return_statement.global_variables
            ret_return_nodes   += fsm_return_statement.return_nodes
            ret_break_nodes    += fsm_return_statement.break_nodes
            ret_continue_nodes += fsm_return_statement.continue_nodes
                
            node_end.transitions.append(FSMTransition([], "", fsm_return_statement.starting_node))
            
            node_end = fsm_return_statement.ending_node
            
        return TO_FSM_Return(
            node_start, node_end, ret_global_vars, 
            ret_return_nodes, ret_break_nodes, ret_continue_nodes
        )
            
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
@dataclass 
class StatementWhile(Statement):
    condition: str
    statements: Statement
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node_start = FSMNode([], [], False)
        node_end = FSMNode([], [])
        ret_global_vars = []
        ret_return_nodes = []
        
        fsm_return_statement = self.statements.to_fsm(fsm_name)
        # for gv in fsm_return_statement.global_variables:
        #         ret_global_vars.append(gv)
        ret_global_vars    += fsm_return_statement.global_variables
        ret_return_nodes   += fsm_return_statement.return_nodes
        
        node_start.transitions.append(FSMTransition([], self.condition, fsm_return_statement.starting_node))
        node_start.transitions.append(FSMTransition([], "", node_end))
        
        # continue statement
        if len(fsm_return_statement.continue_nodes) > 0:
            # clear all extra transitions and point all the node to continue node
            for continue_node in fsm_return_statement.continue_nodes:
                continue_node.transitions.clear()
                continue_node.transitions.append(FSMTransition([], "", node_start))
        
        # break statement
        if len(fsm_return_statement.break_nodes) > 0:
            # clear all extra transitions and point all the node to break node
            for break_node in fsm_return_statement.break_nodes:
                break_node.transitions.clear()
                break_node.transitions.append(FSMTransition([], "", node_end))
                
            # multiple node will point to end node, then the end node will be uncollapsible
            node_end.collapsible = False
        
        fsm_return_statement.ending_node.transitions.append(FSMTransition([], "", node_start))
        
        return TO_FSM_Return(node_start, node_end, ret_global_vars, ret_return_nodes, [], [])
        
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
 
@dataclass 
class StatementDoWhile(Statement):
    condition: str
    statements: Statement
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node_start = FSMNode([], [], False)
        node_end = FSMNode([], [])
        ret_global_vars = []
        ret_return_nodes = []
        
        fsm_return_statement = self.statements.to_fsm(fsm_name)
        # for gv in fsm_return_statement.global_variables:
        #         ret_global_vars.append(gv)
        ret_global_vars    += fsm_return_statement.global_variables
        ret_return_nodes   += fsm_return_statement.return_nodes
                
        node_start.transitions.append(FSMTransition([], "", fsm_return_statement.starting_node))
        
        fsm_return_statement.ending_node.transitions.append(FSMTransition([], self.condition, node_start))
        fsm_return_statement.ending_node.transitions.append(FSMTransition([], "", node_end))
        
        # continue statement
        if len(fsm_return_statement.continue_nodes) > 0:
            # clear all extra transitions and point all the node to continue node
            for continue_node in fsm_return_statement.continue_nodes:
                continue_node.transitions.clear()
                continue_node.transitions.append(FSMTransition([], "", node_start))
        
        # break statement
        if len(fsm_return_statement.break_nodes) > 0:
            # clear all extra transitions and point all the node to break node
            for break_node in fsm_return_statement.break_nodes:
                break_node.transitions.clear()
                break_node.transitions.append(FSMTransition([], "", node_end))
                
            # multiple node will point to end node, then the end node will be uncollapsible
            node_end.collapsible = False
            
        return TO_FSM_Return(node_start, node_end, ret_global_vars, ret_return_nodes, [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
@dataclass
class StatementFor(Statement):
    initialization: Statement
    condition: str
    update: Statement
    statements: Statement
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node_start = FSMNode([], [])
        
        node_loop_start = FSMNode([], [], False)
        node_end = FSMNode([], [])
        ret_global_vars = []
        ret_return_nodes = []
        
        fsm_return_initialization = self.initialization.to_fsm(fsm_name)
        # for gv in fsm_return_initialization.global_variables:
        #         ret_global_vars.append(gv)
        ret_global_vars += fsm_return_initialization.global_variables
                
        fsm_return_update = self.update.to_fsm(fsm_name)
        # for gv in fsm_return_update.global_variables:
        #         ret_global_vars.append(gv)
        ret_global_vars += fsm_return_update.global_variables
        
        fsm_return_statement = self.statements.to_fsm(fsm_name)
        # for gv in fsm_return_statement.global_variables:
        #         ret_global_vars.append(gv)
        ret_global_vars += fsm_return_statement.global_variables
        ret_return_nodes   += fsm_return_statement.return_nodes
                
        node_start.transitions.append(FSMTransition([], "", fsm_return_initialization.starting_node))
        fsm_return_initialization.ending_node.transitions.append(FSMTransition([], "", node_loop_start))
        
        node_loop_start.transitions.append(FSMTransition([], self.condition, fsm_return_statement.starting_node))
        node_loop_start.transitions.append(FSMTransition([], "", node_end))
        
        fsm_return_statement.ending_node.transitions.append(FSMTransition([], "", fsm_return_update.starting_node))
        fsm_return_update.ending_node.transitions.append(FSMTransition([], "", node_loop_start))
        
        # continue statement
        if len(fsm_return_statement.continue_nodes) > 0:
            # clear all extra transitions and point all the node to continue node
            for continue_node in fsm_return_statement.continue_nodes:
                continue_node.transitions.clear()
                continue_node.transitions.append(FSMTransition([], "", node_start))
        
        # break statement
        if len(fsm_return_statement.break_nodes) > 0:
            # clear all extra transitions and point all the node to break node
            for break_node in fsm_return_statement.break_nodes:
                break_node.transitions.clear()
                break_node.transitions.append(FSMTransition([], "", node_end))
                
            # multiple node will point to end node, then the end node will be uncollapsible
            node_end.collapsible = False
        
        return TO_FSM_Return(node_start, node_end, ret_global_vars, ret_return_nodes, [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass

@dataclass
class IfCase():
    """ indicating else case when condition == "" """
    condition: str
    statements: Statement

@dataclass
class StatementIf(Statement):
    cases: list[IfCase]
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node_start = FSMNode([], [])
        node_end = FSMNode([], [], False)
        ret_global_vars = []
        
        ret_return_nodes = []
        ret_break_nodes = []
        ret_continue_nodes = []
        
        is_else_case_avaliable = False
        
        for case in self.cases:
            if case.condition == "":
                # this is else case
                is_else_case_avaliable = True
            
            fsm_return_statement = case.statements.to_fsm(fsm_name)
            # for gv in fsm_return_statement.global_variables:
            #         ret_global_vars.append(gv)   
            ret_global_vars    += fsm_return_statement.global_variables
            ret_return_nodes   += fsm_return_statement.return_nodes
            ret_break_nodes    += fsm_return_statement.break_nodes
            ret_continue_nodes += fsm_return_statement.continue_nodes        
                    
                    
            node_start.transitions.append(FSMTransition([], case.condition, fsm_return_statement.starting_node))
            fsm_return_statement.ending_node.transitions.append(FSMTransition([], "", node_end))
            
        if not is_else_case_avaliable: 
            node_start.transitions.append(FSMTransition([], "", node_end))
        
        return TO_FSM_Return(node_start, node_end, ret_global_vars, ret_return_nodes, ret_break_nodes, ret_continue_nodes)
    
    def print_pretty(self, indentation:int=0) -> str:
        pass

@dataclass
class StatementDeclaration(Statement):
    datatype: str
    variable: str
    make_global: bool = False
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        if self.make_global:
            node = FSMNode([], [])
            global_var = FSMGlobalVar(self.datatype, self.variable)
            return TO_FSM_Return(node, node, [global_var], [], [], [])
        else:
            node = FSMNode([code_template.DECLARE_LOCAL_VARIABLE(self.datatype, self.variable)], [])
            return TO_FSM_Return(node, node, [], [], [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass

@dataclass
class StatementDeclarationInit(Statement):
    datatype: str
    variable: str
    expression: str
    make_global: bool = False
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        if self.make_global:
            node = FSMNode([code_template.LOCAL_VARIABLE_ASSIGNMENT(self.variable, self.expression)], [])
            global_var = FSMGlobalVar(self.datatype, self.variable)
            return TO_FSM_Return(node, node, [global_var], [], [], [])
        else:
            node = FSMNode([code_template.DECLARE_LOCAL_VARIABLE_INIT(self.datatype, self.variable, self.expression)], [])
            return TO_FSM_Return(node, node, [], [], [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
@dataclass
class StatementWait(Statement):
    """ set `wait_time_ms` to "" to indicate YIELD """
    wait_time_ms: str
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        fsm_name = "" if fsm_name is None else fsm_name
        
        if self.wait_time_ms == "":
            # YIELD statement
            node = FSMNode([], [], False, "true") # the program will always entry this node, no block. 
            # this helps the optimization
            return TO_FSM_Return(node, node, [], [], [], [])
        else:
            # WAIT statement
            node_register_time = FSMNode([code_template.REGISTER_TIME(fsm_name)], [])
            node_entry_until = FSMNode([], [], False, code_template.IS_TIME_PASSED(fsm_name, self.wait_time_ms))
            
            node_register_time.transitions.append(FSMTransition([], "", node_entry_until))
            
            return TO_FSM_Return(node_register_time, node_entry_until, [], [], [], [])
            
    
    def print_pretty(self, indentation:int=0) -> str:
        pass

@dataclass
class StatementWaitUnless(Statement):
    condition: str  
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node = FSMNode([], [], False, self.condition)
        return TO_FSM_Return(node, node, [], [], [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
@dataclass
class StatementBreak(Statement): 
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node = FSMNode([], [])
        return TO_FSM_Return(node, node, [], [], [node], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
class StatementContinue(Statement): 
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node = FSMNode([], [])
        return TO_FSM_Return(node, node, [], [], [], [node])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    
class StatementReturn(Statement): 
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        node = FSMNode([], [])
        return TO_FSM_Return(node, node, [], [node], [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
    

@dataclass
class ParseResult(Statement):
    function_name: str
    statements: StatementBlock
    
    def to_fsm(self, fsm_name:str|None=None) -> TO_FSM_Return:
        """Generate Raw FSM

        Parameters
        ----------
        fsm_name : str | None, optional
            This variable can be any value and does not effect any functionality of this function.  
            The existance of this variable is override the inheritant method, Statement.to_fsm(self, fsm_name:str|None=None).  
            by default None

        Returns
        -------
        TO_FSM_Return
            Function return value. 
            - starting node
            - ending node
            - list of global variables
            - return_nodes: list[FSMNode] <- This should be empty
            - break_nodes: list[FSMNode] <- This should be empty
            - continue_nodes: list[FSMNode] <- This should be empty
        """
        
        fsm_name = self.function_name
        
        node_start = FSMNode([], [], False)
        node_end = FSMNode([], [], False) 
        ret_global_vars = []
        
        fsm_return_statement = self.statements.to_fsm(fsm_name)
        # for gv in fsm_return_statement.global_variables:
        #     ret_global_vars.append(gv)
        ret_global_vars    += fsm_return_statement.global_variables
        
            
        node_start.transitions.append(FSMTransition([], "", fsm_return_statement.starting_node))
        fsm_return_statement.ending_node.transitions.append(FSMTransition([], "", node_end))
        
        # continue statement
        if len(fsm_return_statement.continue_nodes) > 0:
            # clear all extra transitions and point all the node to continue node
            for continue_node in fsm_return_statement.continue_nodes:
                continue_node.transitions.clear()
                continue_node.transitions.append(FSMTransition([], "", node_start))
        
        # break statement
        if len(fsm_return_statement.break_nodes) > 0:
            # clear all extra transitions and point all the node to break node
            for break_node in fsm_return_statement.break_nodes:
                break_node.transitions.clear()
                break_node.transitions.append(FSMTransition([], "", node_end))
           
        # return statement
        if len(fsm_return_statement.return_nodes) > 0:
            # clear all extra transitions and point all the node to break node
            for return_node in fsm_return_statement.return_nodes:
                return_node.transitions.clear()
                return_node.transitions.append(FSMTransition([], "", node_end))     
            
        
        return TO_FSM_Return(node_start, node_end, ret_global_vars, [], [], [])
    
    def print_pretty(self, indentation:int=0) -> str:
        pass
