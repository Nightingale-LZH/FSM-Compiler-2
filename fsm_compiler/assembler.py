import logging
logger = logging.getLogger(__name__)

from .ast_types import *

def traverse_fsm(fsm_starting_node:FSMNode) -> set[FSMNode]:
    """get set of all accessable node

    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node

    Returns
    -------
    set[FSMNode]
        return a set of all accessible node
    """
    ret_val: set[FSMNode] = set()
    
    search_queue: list[FSMNode] = []
    
    search_queue.append(fsm_starting_node)
    while len(search_queue) != 0:
        node_curr = search_queue.pop(0) 
        
        ret_val.add(node_curr)
        
        for transition in node_curr.transitions:
            node_next: FSMNode = transition.target_node
            
            if node_next not in ret_val:
                search_queue.append(node_next)
    
    return ret_val

def trace_back_transition(fsm_node: FSMNode, fsm_starting_node: FSMNode) -> list[FSMTransition]:
    """get all transition to `fsm_node`

    Parameters
    ----------
    fsm_node : FSMNode
        the node that is being searched for transition
    fsm_starting_node : FSMNode
        the start of the fsm

    Returns
    -------
    list[FSMTransition]
        a list of transition that targetted to the `fsm_node`. the order is random
    """
                
    return [
        transition
        for node in traverse_fsm(fsm_starting_node)
        for transition in node.transitions
        if id(transition.target_node) == id(fsm_node)
    ]
    
def check_wait_statement_usage(fsm_starting_node: FSMNode) -> bool:
    """Check if WAIT(int ms) statement is used
    
    This function is used to ensure whether generate timer counter for WAIT statement
    
    **NOTE: This function is most stable when operating on unoptimized fsm**

    Parameters
    ----------
    fsm_starting_node : FSMNode
        the start of the fsm

    Returns
    -------
    bool
        return if WAIT statement is used. 
    """
    generated_wait_statement = code_template.IS_TIME_PASSED("", "")[:-5] # __IS_TIME_PASSED
    
    for state in traverse_fsm(fsm_starting_node):
        if generated_wait_statement in state.entry_condition:
            # contains code that implementing WAIT() stmt
            return True
    
    return False

def convert_to_raw_state_machine(parse_result: ParseResult) -> FSMMachine:
    """Unclapsed finite state machine

    Parameters
    ----------
    parse_result : ParseResult
        Resulting AST from parser

    Returns
    -------
    FSMMachine
        The result finite state machine
        - global code block
        - global variables
        - starting node of fsm
    """
    fsm_return = parse_result.to_fsm()
    global_code_block = []
    if check_wait_statement_usage(fsm_return.starting_node):
        # add timer variable declaration
        global_code_block.append(code_template.DECLARE_TIME_VARIABLE(fsm_name=parse_result.function_name))
        
    return FSMMachine(
        fsm_return.global_variables, global_code_block, fsm_return.starting_node, parse_result.function_name
    )
    
def get_ending_node_of_fsm(fsm_starting_node:FSMNode) -> FSMNode|None:
    """Get the ending node of the given fsm

    Parameters
    ----------
    fsm_starting_node : FSMNode
        the start of the fsm

    Returns
    -------
    FSMNode|None
        return the ending node of ths fsm
        return None if something is wrong
    """
    for state in traverse_fsm(fsm_starting_node):
        if len(state.transitions) == 0:
            return state
    return None
    
def generate_FSM_from_AST(parse_result: ParseResult, optimization_level:int=4) -> FSMMachine:
    """Generate fsm from parsed AST, and optimize the returning fsm
    
    optimization level details: 
        1. optimize consecutive states
        2. optimize chained empty state, and all above
        3. optimize chained branching, and all above
        4. optimize chained merging, and all above
        5. optimize consecutive uncollapsible states, and all above

    Parameters
    ----------
    parse_result : ParseResult
        Resulting AST from parser
    optimization_level : int, optional
        optimization level of the FSM, by default 5  
        - 0 is no optimization, 
        - 5 is all context-free optimization

    Returns
    -------
    FSMMachine
        The result finite state machine
        - global code block
        - global variables
        - starting node of fsm
    """
    
    ret_val = convert_to_raw_state_machine(parse_result)
    optimize_fsm(ret_val.starting_node, optimization_level)
    
    return ret_val

# -------------------------------------------------- #
#        Context-free Optimization Strategy          #
# -------------------------------------------------- #

def optimize_fsm_consecutive_states(fsm_starting_node:FSMNode) -> bool:
    """optimize consecutive states
    
    collapse if 
        - it only have one transition to next node, and
        - the only transition doesn't have condition, and
        - it's next node is collapsible
    
    this function will modifiy the given fsm. Does NOT return a new FSM
    
    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node

    Returns
    -------
    bool
        If the fsm is modified at all
    """
    
    # implement fix-point algorithm
    
    has_modified = True
    while (has_modified):
        has_modified = False
        has_modified_master = False
        
        searched_nodes: set[FSMNode] = set()
    
        search_queue: list[FSMNode] = []
        
        search_queue.append(fsm_starting_node)
        while len(search_queue) != 0:
            node_curr = search_queue.pop(0) 
            
            searched_nodes.add(node_curr)
            
            # collapse if 
            #   - it only have one transition to next node, and
            #   - the only transition doesn't have condition, and
            #   - it's next node is collapsible
            
            if len(node_curr.transitions) == 0:
                continue
            elif len(node_curr.transitions) == 1:
                # if it's next node is collapsible and transition condition is "", then collapse
                
                transition: FSMTransition = node_curr.transitions[0]
                node_next: FSMNode = transition.target_node
                assert len(transition.code_block) == 0 # the generated fsm will never have mealy transition
                
                if transition.condition == "" and node_next.collapsible:
                    # collapse curr and next nodes
                    if len(node_curr.code_block) == 0:
                        node_curr.code_block = node_next.code_block
                    else:
                        if len(node_next.code_block) > 0:
                            node_curr.code_block += node_next.code_block
                    
                    node_curr.transitions = node_next.transitions
                    
                    has_modified = True
                    has_modified_master = True
                    break
                
                else: 
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
            else:
                for transition in node_curr.transitions:
                    node_next: FSMNode = transition.target_node
                    
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
    
    return has_modified_master
    
def optimize_fsm_chained_empty_state(fsm_starting_node:FSMNode) -> bool:
    """optimize chained empty state
    
    collapse if
        - current node is collapsible
        - current node has empty code block
        - current node only has one transition to next node
        - current node only has one traced back transition
        - the transition to next node does not have transition condition
        - the next node does not have entry condition
    
    this function will modifiy the given fsm. Does NOT return a new FSM
    
    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node

    Returns
    -------
    bool
        If the fsm is modified at all
    """
    
    # implement fix-point algorithm
    
    has_modified = True
    while (has_modified):
        has_modified = False
        has_modified_master = False
        
        searched_nodes: set[FSMNode] = set()
    
        search_queue: list[FSMNode] = []
        
        search_queue.append(fsm_starting_node)
        while len(search_queue) != 0:
            node_curr = search_queue.pop(0) 
            
            searched_nodes.add(node_curr)
            
            # collapse if 
            #   - current node is collapsible
            #   - current node has empty code block
            #   - current node only has one transition to next node
            #   - current node only has one traced back transition
            #   - the transition to next node does not have transition condition
            #   - the next node does not have entry condition
            
            if len(node_curr.transitions) == 0:
                continue
            elif len(node_curr.transitions) == 1:
                # collapse if 
                #   - current node is collapsible
                #   - current node has empty code block
                #   - current node only has one traced back transition
                #   - the transition to next node does not have transition condition
                #   - the next node does not have entry condition
                
                traced_back_transitions = trace_back_transition(node_curr, fsm_starting_node)
                transition: FSMTransition = node_curr.transitions[0]
                node_next: FSMNode = transition.target_node
                assert len(transition.code_block) == 0 # the generated fsm will never have mealy transition
                
                if (
                    node_curr.collapsible 
                    and len(node_curr.code_block) == 0 
                    and transition.condition == ""
                    and node_next.entry_condition == ""
                    and len(traced_back_transitions) == 1
                ):
                    # collapse curr and next nodes
                    traced_back_transitions[0].target_node = node_next
                    
                    has_modified = True
                    has_modified_master = True
                    break
                
                else: 
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
            else:
                for transition in node_curr.transitions:
                    node_next: FSMNode = transition.target_node
                    
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
    
    return has_modified_master

def optimize_fsm_chained_branching(fsm_starting_node:FSMNode) -> bool:
    """optimize chained branching
    
    collapse if
        - current has a else condition (the last transition without transition condition) to the next node
        - the next node is collapsible
        - the next node has no entry condition
        - the next node is also a braching node, i.e. has more than two transition
        - the next node doesn't have code block
    
    fun fact, this also optimized 
        - `IF (...) { ... } ELSE IF (...) { ... } ...`
        - `WHILE(...) { ...} IF (...) { ... }`
        - etc.
    
    this function will modifiy the given fsm. Does NOT return a new FSM
    
    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node

    Returns
    -------
    bool
        If the fsm is modified at all
    """
    
    # implement fix-point algorithm
    
    has_modified = True
    while (has_modified):
        has_modified = False
        has_modified_master = False
        
        searched_nodes: set[FSMNode] = set()
    
        search_queue: list[FSMNode] = []
        
        search_queue.append(fsm_starting_node)
        while len(search_queue) != 0:
            node_curr = search_queue.pop(0) 
            
            searched_nodes.add(node_curr)
            
            # collapse if 
            # - current has a else condition (the last transition without transition condition) to the next node
            # - the next node is collapsible
            # - the next node has no entry condition
            # - the next node is also a braching node, i.e. has more than two transition
            # - the next node doesn't have code block
            
            if len(node_curr.transitions) == 0:
                continue
            elif len(node_curr.transitions) == 1:
                node_next: FSMNode = node_curr.transitions[0].target_node
                if node_next not in searched_nodes:
                    search_queue.append(node_next)
            else:
                if node_curr.transitions[-1].condition == "": # else statement
                    # collapse if 
                    # - the next node is collapsible
                    # - the next node has no entry condition
                    # - the next node is also a braching node, i.e. has more than two transition    
                    # - the next node doesn't have code block
                    node_next: FSMNode = node_curr.transitions[-1].target_node
                    
                    if (
                        len(node_next.code_block) == 0
                        and node_next.entry_condition == ""
                        and len(node_next.transitions) >= 2
                        and node_next.collapsible
                    ):
                        node_curr.transitions.pop(-1)
                        node_curr.transitions += node_next.transitions
                        
                        has_modified = True
                        has_modified_master = True
                        break
                
                for transition in node_curr.transitions:
                    node_next: FSMNode = transition.target_node
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
    
    return has_modified_master

def optimize_fsm_chained_merging(fsm_starting_node:FSMNode) -> bool:
    """optimize chained merging
    
    WARNING, this might collapse uncollapsible nodes.
    
    collapse if
        - current node has empty code block
        - current node has no entry condition
        - current node has exactly one transition to next 
        - current node's only one transition has no condition
        - next node has equal or greater one transition to the next next, aka not ending node
        - next node has no entry condition
    
    fun fact, this also optimized 
        - `IF (...) { ... } ELSE IF (...) { ... } ...`
        - `WHILE(...) { ...} IF (...) { ... }`
        - etc.
    
    this function will modifiy the given fsm. Does NOT return a new FSM
    
    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node

    Returns
    -------
    bool
        If the fsm is modified at all
    """
    
    # implement fix-point algorithm
    
    has_modified = True
    while (has_modified):
        has_modified = False
        has_modified_master = False
        
        searched_nodes: set[FSMNode] = set()
    
        search_queue: list[FSMNode] = []
        
        search_queue.append(fsm_starting_node)
        while len(search_queue) != 0:
            node_curr = search_queue.pop(0) 
            
            searched_nodes.add(node_curr)
            
            # collapse if
            #     - current node has empty code block
            #     - current node has no entry condition
            #     - current node has exactly one transition to next 
            #     - current node's only one transition has no condition
            #     - next node has equal or greater one transition to the next next
            #     - next node has no entry condition
            
            if len(node_curr.transitions) == 0:
                continue
            elif len(node_curr.transitions) == 1:
                # collapse if
                #     - current node is not initial state, trace back transition of current node >= 1
                #     - current node has empty code block
                #     - current node has no entry condition
                #     - current node's only one transition has no condition
                #     - next node has equal or greater one transition to the next next
                #     - next node has no entry condition
                
                transition: FSMTransition = node_curr.transitions[0]
                node_next: FSMNode = transition.target_node
                assert len(transition.code_block) == 0 # the generated fsm will never have mealy transition
                
                if (
                    len(node_curr.code_block) == 0
                    and node_curr.entry_condition == ""
                    and transition.condition == ""
                    and len(node_next.transitions) >= 1
                    and node_next.entry_condition == ""
                ):
                    back_transitions = trace_back_transition(node_curr, fsm_starting_node)
                    
                    if len(back_transitions) > 0: 
                        # not starting node, by pass current node
                        for back_transition in back_transitions:
                            back_transition.target_node = node_next
                        
                    else:
                        # this is the starting node, merge starting node and next node
                        node_curr.transitions = node_next.transitions
                        node_curr.collapsible = node_next.collapsible
                        node_curr.code_block = node_next.code_block
                        
                        node_next_back_transitions = trace_back_transition(node_next, fsm_starting_node)
                        for back_transition in node_next_back_transitions:
                            back_transition.target_node = node_curr
                        
                    
                    has_modified = True
                    has_modified_master = True
                    break
                
                else: 
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
            else:
                for transition in node_curr.transitions:
                    node_next: FSMNode = transition.target_node
                    
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
    
    return has_modified_master


def is_truly_collapsible(fsm_node:FSMNode, fsm_starting_node:FSMNode) -> bool:
    """determine if the node is truly collapsible, ignore the collapsible field

    The node is collapsible if
        - only one trace-back-transition
        - the trace-back-transition does not have transition condition
        - does not have entry condition
        - the node has equal or greater than 1 transitions to other nodes (so, this is not end node)
        - the node is not beginning node
        
    Parameters
    ----------
    fsm_node : FSMNode
        Determined Node
    fsm_starting_node : FSMNode
        Starting Node

    Returns
    -------
    bool
        determine if the node is truly collapsible
    """
    traced_back_transitions = trace_back_transition(fsm_node, fsm_starting_node)
    
    return (
        len(traced_back_transitions) == 1
        and traced_back_transitions[0].condition == ""
        and fsm_node.entry_condition == ""
        and len(fsm_node.transitions) >= 1
        and id(fsm_node) != id(fsm_starting_node)
    )


def optimize_fsm_consecutive_uncollapsible_states(fsm_starting_node:FSMNode) -> bool:
    """optimize consecutive uncollapsible states
    
    This optimization strategy is primary aim for less optimized structure created by BREAK, CONTINUE, 
    and RETURN. 
    
    collapse if 
        - it only have one transition to next node, and
        - the only transition doesn't have condition, and
        - its next node is collapsible
        
    However, this function will trace back transitions from a node to determine if the node is collapsible, 
    rather than following the labeled collapsible. This function might over optimize the FSM, so Use it with 
    caution. 
    
    The node is collapsible if
        - only one trace-back-transition
        - does not have entry condition
        - the node has more than 1 transitions to other nodes (so, this is not end node)
    
    this function will modifiy the given fsm. Does NOT return a new FSM
    
    Parameters
    ----------
    fsm_starting_node : FSMNode
        Starting Node

    Returns
    -------
    bool
        If the fsm is modified at all
    """
    
    # implement fix-point algorithm
    
    has_modified = True
    while (has_modified):
        has_modified = False
        has_modified_master = False
        
        searched_nodes: set[FSMNode] = set()
    
        search_queue: list[FSMNode] = []
        
        search_queue.append(fsm_starting_node)
        while len(search_queue) != 0:
            node_curr = search_queue.pop(0) 
            
            searched_nodes.add(node_curr)
            
            # collapse if 
            #   - it only have one transition to next node, and
            #   - the only transition doesn't have condition, and
            #   - it's next node is collapsible
            
            if len(node_curr.transitions) == 0:
                continue
            elif len(node_curr.transitions) == 1:
                # if it's next node is collapsible and transition condition is "", then collapse
                
                transition: FSMTransition = node_curr.transitions[0]
                node_next: FSMNode = transition.target_node
                assert len(transition.code_block) == 0 # the generated fsm will never have mealy transition
                
                if transition.condition == "" and is_truly_collapsible(node_next, fsm_starting_node):
                    # collapse curr and next nodes
                    if len(node_curr.code_block) == 0:
                        node_curr.code_block = node_next.code_block
                    else:
                        if len(node_next.code_block) > 0:
                            node_curr.code_block += node_next.code_block
                    
                    node_curr.transitions = node_next.transitions
                    
                    has_modified = True
                    has_modified_master = True
                    break
                
                else: 
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
            else:
                for transition in node_curr.transitions:
                    node_next: FSMNode = transition.target_node
                    
                    if node_next not in searched_nodes:
                        search_queue.append(node_next)
    
    return has_modified_master


# -------------------------------------------------- #
#                 FSM Optimization                   #
# -------------------------------------------------- #

OPTIMIZATION_STRATEGIES = {
    1: optimize_fsm_consecutive_states,
    2: optimize_fsm_chained_empty_state,
    3: optimize_fsm_chained_branching,
    4: optimize_fsm_chained_merging,
    5: optimize_fsm_consecutive_uncollapsible_states,
}
    
def optimize_fsm(fsm_starting_node:FSMNode, opt_level:int=5) -> None:
    opt_level = min(opt_level, len(OPTIMIZATION_STRATEGIES))
    is_changed = True
    while (is_changed):
        is_changed = False
        for level in range(1, opt_level + 1):
            while OPTIMIZATION_STRATEGIES[level](fsm_starting_node):
                is_changed = True


