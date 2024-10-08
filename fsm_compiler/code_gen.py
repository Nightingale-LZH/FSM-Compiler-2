import logging
logger = logging.getLogger(__name__)

from .ast_types import *
from . import assembler
from . import code_template

from dataclasses import dataclass

# ====================================================================== #
#                          BARE FSM OPERATIONS                           #
# ====================================================================== #

# -------------------------------------------------- #
#                       Mermaid                      #
# -------------------------------------------------- #

def purge_code_as_mermaid_commend(code:str) -> str:
    """replace 
    - `"` as `''` 
    - `\\` as `\\\\`
    
    """
    return code.replace('"', "''").replace("\\", "\\\\")

def fsm_to_mermaid(fsm_starting_node:FSMNode, debug:bool=False, global_variables:list[FSMGlobalVar]|None=None) -> str:
    """return a string that illustrate the fsm in mermaid 

    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node
        
    debug : bool
        Turn on the debugging information (distinguish collapsible states), by default, False

    Returns
    -------
    str
        return a string that illustrate the fsm in mermaid 
    """
    states = assembler.traverse_FSM(fsm_starting_node)
    
    ret_val = "```mermaid\nflowchart TB\n"
    
    for state in states:
        
        if debug:
            state_shape = ("[[", "]]") if id(state) == id(fsm_starting_node) else ("([", "])") if state.collapsible else ("[", "]") 
        else:
            state_shape = ("[[", "]]") if id(state) == id(fsm_starting_node) else ("[", "]") 
        
        if state.entry_condition == "":
            if len(state.code_block) == 0:
                ret_val += '   {}{}_{}\n'.format(
                    id(state), 
                    state_shape[0], 
                    state_shape[1]
                ) 
            else:
                ret_val += '   {}{}"`{}`"{}\n'.format(
                    id(state), 
                    state_shape[0], 
                    purge_code_as_mermaid_commend("\n".join(state.code_block)), 
                    state_shape[1]
                ) 
        else:
            if len(state.code_block) == 0:
                ret_val += '   {}{}"`ENTRY: {}`"{}\n'.format(
                    id(state), 
                    state_shape[0], 
                    purge_code_as_mermaid_commend(state.entry_condition), 
                    state_shape[1]
                ) 
            else:
                ret_val += '   {}{}"`ENTRY: {}\n{}`"{}\n'.format(
                    id(state), 
                    state_shape[0], 
                    purge_code_as_mermaid_commend(state.entry_condition), 
                    purge_code_as_mermaid_commend("\n".join(state.code_block)), 
                    state_shape[1]
                ) 
      
    ret_val += "\n"
    for state in states:
        for transition in state.transitions:
            if transition.condition == "":
                if len(transition.code_block) == 0:
                    ret_val += '   {} --> {}\n'.format(
                        id(state), 
                        id(transition.target_node)
                    ) 
                else:
                    ret_val += '   {} -->|"`*------*\n{}`"| {}\n'.format(
                        id(state), 
                        purge_code_as_mermaid_commend("\n".join(transition.code_block)), 
                        id(transition.target_node)
                    ) 
            else: 
                if len(transition.code_block) == 0:
                    ret_val += '   {} -->|"`{}`"| {}\n'.format(
                        id(state), 
                        purge_code_as_mermaid_commend(transition.condition), 
                        id(transition.target_node)
                    ) 
                else:
                    ret_val += '   {} -->|"`{}\n*------*\n{}`"| {}\n'.format(
                        id(state), 
                        purge_code_as_mermaid_commend(transition.condition), 
                        purge_code_as_mermaid_commend("\n".join(transition.code_block)), 
                        id(transition.target_node)
                    ) 
                    
    if global_variables is not None:
        ret_val +='\n    global_vars["`Global Variables\n'
        for global_variable in global_variables:
            ret_val += "        {} {};\n".format(global_variable.var_type, global_variable.var_name)
        ret_val += '    `"]\n'
        
    ret_val += "```"
    return ret_val


# -------------------------------------------------- #
#                      Graphviz                      #
# -------------------------------------------------- #

def purge_code_as_graphviz_dot_commend(code:str) -> str:
    """replace 
    - `"` as `''` 
    - `\\` as `\\\\`
    
    """
    return code.replace('"', "''").replace("\\", "\\\\")

def fsm_to_graphviz_dot(fsm_starting_node:FSMNode, debug:bool=False, global_variables:list[FSMGlobalVar]|None=None) -> str:
    """return a string that illustrate the fsm in graphviz, using DOT language 

    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node
        
    debug : bool
        Turn on the debugging information (distinguish collapsible states), by default, False

    Returns
    -------
    str
        return a string that illustrate the fsm in graphviz, using DOT language 
    """
    
    STATE_LABEL = lambda node: "s{}".format(id(node))
    
    states = assembler.traverse_FSM(fsm_starting_node)
    
    ret_val = "digraph {\n"
    
    for state in states:
        if debug:
            state_shape = "Msquare" if id(state) == id(fsm_starting_node) else "ellipse" if state.collapsible else "rect"
        else:
            state_shape = "Msquare" if id(state) == id(fsm_starting_node) else "rect"
        
        if state.entry_condition == "":
            if len(state.code_block) == 0:
                ret_val += '   {} [shape={}, label="_"];\n'.format(
                    STATE_LABEL(state), 
                    state_shape
                ) 
            else:
                ret_val += '   {} [shape={}, label="{}"];\n'.format(
                    STATE_LABEL(state), 
                    state_shape,
                    "\\n".join([purge_code_as_graphviz_dot_commend(line) for line in state.code_block]), 
                ) 
        else:
            if len(state.code_block) == 0:
                ret_val += '   {} [shape={}, label="ENTRY: {}"];\n'.format(
                    STATE_LABEL(state), 
                    state_shape,
                    purge_code_as_graphviz_dot_commend(state.entry_condition), 
                ) 
            else:
                ret_val += '   {} [shape={}, label="ENTRY: {}\\n{}"];\n'.format(
                    STATE_LABEL(state), 
                    state_shape,
                    purge_code_as_graphviz_dot_commend(state.entry_condition), 
                    "\\n".join([purge_code_as_graphviz_dot_commend(line) for line in state.code_block]), 
                ) 
      
    ret_val += "\n"
    for state in states:
        for transition in state.transitions:
            if transition.condition == "":
                if len(transition.code_block) == 0:
                    ret_val += '   {} -> {};\n'.format(
                        STATE_LABEL(state), 
                        STATE_LABEL(transition.target_node)
                    ) 
                else:
                    ret_val += '   {} -> {} [label="-----\\n{}"];\n'.format(
                        STATE_LABEL(state), 
                        STATE_LABEL(transition.target_node),
                        "\\n".join([purge_code_as_graphviz_dot_commend(line) for line in transition.code_block]), 
                    ) 
            else: 
                if len(transition.code_block) == 0:
                    ret_val += '   {} -> {} [label="{}"];\n'.format(
                        STATE_LABEL(state), 
                        STATE_LABEL(transition.target_node),
                        purge_code_as_graphviz_dot_commend(transition.condition), 
                    ) 
                else:
                    ret_val += '   {} -> {} [label="{}\\n-----\\n{}"];\n'.format(
                        STATE_LABEL(state), 
                        STATE_LABEL(transition.target_node),
                        purge_code_as_graphviz_dot_commend(transition.condition), 
                        "\\n".join([purge_code_as_graphviz_dot_commend(line) for line in transition.code_block]), 
                    ) 
    
    if global_variables is not None:
        ret_val +='\n    global_vars [shape=rect, label="Global Variables\\n'
        for global_variable in global_variables:
            ret_val += "{} {};\\n".format(global_variable.var_type, global_variable.var_name)
        ret_val += '"]\n'
    
    ret_val += "}"
    return ret_val

# ====================================================================== #
#                         PACKAGED FSM OPERATIONS                        #
# ====================================================================== #
# -------------------------------------------------- #
#                     C++ Code Gen                   #
# -------------------------------------------------- #

def generate_code_from_FSM(
    fsm:FSMMachine, 
    generate_fix_iteration_function:bool=True, 
    generate_minimum_timed_function:bool=True,
) -> str:
    """Generate Code from Given FSM
    
    Optionally, the code will contain addtional FSM entry points that faciliate the FSM scheduling.

    Parameters
    ----------
    fsm : FSMMachine
        Finite State Machine from Assembler process
    generate_fix_iteration_function : bool, optional
        The FSM entry point that run the FSM for given fix number of times, 
        by default True
    generate_minimum_timed_function : bool, optional
        The FSM entry that run the FSM for minimum given millisecond, 
        by default True

    Returns
    -------
    str
        C/C++ Code
    """    
    
    state_to_int:dict[FSMNode, int] = {}
    
    starting_state = fsm.starting_node
    ending_state = assembler.get_ending_node_of_FSM(starting_state)
    
    states = assembler.traverse_FSM(starting_state)
    
    state_counter = 10
    for state in states:
        if state == starting_state:
            state_to_int[state] = 0
        elif state == ending_state:
            state_to_int[state] = 1
        else:
            state_to_int[state] = state_counter
            state_counter += 1
    
    # sort the list of state by the numbers
    states_list: list[tuple[int, FSMNode]] = [
        (state_number, state)
        for state, state_number in state_to_int.items()
    ]
    states_list.sort(key=lambda elmt: elmt[0])
    
    
    # generate global statements
    global_stmt:list[code_template.CPP_CODE_RenderingTemplate] = []
    
    for gvar in fsm.global_variables:
        global_stmt.append(
            code_template.CPP_CODE_GlobalStatements(code_template.DECLARE_GLOBAL_VARIABLE(gvar.var_type, gvar.var_name))
        )
        
    for code_line in fsm.global_code_block:
        global_stmt.append(
            code_template.CPP_CODE_GlobalStatements(code_line)
        )
    
    # generate state statements
    states_stmt:list[code_template.CPP_CODE_RenderingTemplate] = []
    
    for _, state in states_list:
        
        # generate state transition statements
        transitions_stmt:list[code_template.CPP_CODE_RenderingTemplate] = []
        for transition in state.transitions:
            transitions_stmt.append(
                code_template.CPP_CODE_Transition(
                    transition.condition, 
                    transition.code_block, 
                    state_to_int[transition.target_node],
                    fsm.fsm_name
                )
            )
            
        states_stmt.append(
            code_template.CPP_CODE_States(
                state_to_int[state],
                state.code_block, 
                state.entry_condition, 
                transitions_stmt, 
                fsm.fsm_name
            )
        )
        
    aux_function_stms: list[code_template.CPP_CODE_RenderingTemplate] = []
    
    if generate_fix_iteration_function:
        aux_function_stms.append(code_template.CPP_CODE_CppFunction_EntryFixedIteration(fsm.fsm_name))
    
    if generate_minimum_timed_function:
        aux_function_stms.append(code_template.CPP_CODE_CppFunction_MinimumTimeIteration(fsm.fsm_name))
        
    # generate fsm function
    cpp_function = code_template.CPP_CODE_CppFunction(
        states_stmt, global_stmt, fsm.fsm_name, aux_function_stms
    )
    
    return cpp_function.render()

# -------------------------------------------------- #
#                      Graphviz                      #
# -------------------------------------------------- #
def generate_graphviz_dot_visualization_from_FSM(fsm:FSMMachine) -> str:
    return fsm_to_graphviz_dot(fsm.starting_node, global_variables=fsm.global_variables)

# -------------------------------------------------- #
#                       Mermaid                      #
# -------------------------------------------------- #
def generate_mermaid_visualization_from_FSM(fsm:FSMMachine) -> str:
    return fsm_to_mermaid(fsm.starting_node, global_variables=fsm.global_variables)