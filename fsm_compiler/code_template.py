import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass

# -------------------------------------------------- #
#     WAIT, WAIT_UNLESS, YIELD statement related     #
# -------------------------------------------------- #
DECLARE_TIME_VARIABLE = lambda fsm_name: "__DECLARE_TIME_VARIABLE({});".format(fsm_name) 
REGISTER_TIME = lambda fsm_name: "__REGISTER_CURRENT_TIME({});".format(fsm_name)
IS_TIME_PASSED = lambda fsm_name, wait_time_ms: "__IS_TIME_PASSED({}, {})".format(fsm_name, wait_time_ms)
    
# -------------------------------------------------- #
#              GLOBAL statement related              #
# -------------------------------------------------- #
DECLARE_LOCAL_VARIABLE = lambda var_type, var_name: "{} {};".format(var_type, var_name)
DECLARE_LOCAL_VARIABLE_INIT = lambda var_type, var_name, initialization: "{} {} = {};".format(var_type, var_name, initialization)
LOCAL_VARIABLE_ASSIGNMENT = lambda var_name, initialization: "{} = {};".format(var_name, initialization)

DECLARE_GLOBAL_VARIABLE = lambda var_type, var_name: "{} {};".format(var_type, var_name)

# -------------------------------------------------- #
#                  C++ code related                  #
# -------------------------------------------------- #
CPP_FSM_META_VARIABLE_DECLARATION = lambda fsm_name: "__FSM_META_VARIABLE_DECLARATION({});".format(fsm_name)
CPP_FUNCTION_HEADER = lambda fsm_name: "void {}() {{".format(fsm_name)

CPP_FUNCTION_FIXED_ITERATION_HEADER = lambda fsm_name: "void {}_fixed_iteration(unsigned int count) {{".format(fsm_name)
CPP_FUNCTION_FIXED_ITERATION_LOOPS = lambda fsm_name: "for (int i = 0; i < count; ++i) {{ {}(); }}".format(fsm_name)

CPP_FUNCTION_MIN_TIME_DECLARE_TIME_VARIABLE = lambda fsm_name: "__DECLARE_MIN_RUNTIME_ITER_TIME_VARIABLE({});".format(fsm_name) 
CPP_FUNCTION_MIN_TIME_REGISTER_TIME = lambda fsm_name: "__REGISTER_MIN_RUNTIME_ITER_CURRENT_TIME({});".format(fsm_name)
CPP_FUNCTION_MIN_TIME_IS_TIME_PASSED = lambda fsm_name, wait_time_ms: "___MIN_RUNTIME_IS_TIME_PASSED({}, {})".format(fsm_name, wait_time_ms)
CPP_FUNCTION_MIN_TIME_ITERATION_HEADER = lambda fsm_name: "void {}_min_runtime(unsigned long ms) {{".format(fsm_name)
CPP_FUNCTION_MIN_TIME_ITERATION_LOOPS = lambda condition: "while(!({})) {{".format(condition)

CPP_STATE_HEADER = lambda fsm_name, state_id: "if (__CURRENT_STATE({}) == {}) {{".format(fsm_name, state_id)
CPP_STATE_ENTRY_CONDITION = lambda entry_condition: "if (!({})) {{ return; }}".format(entry_condition)

CPP_TRANSITION_HEADER = lambda condition: "if ({}) {{".format(condition)
CPP_CHANGE_STATE = lambda fsm_name, next_node_id: "__CHANGE_STATE({}, {});".format(fsm_name, next_node_id)


@dataclass
class CPP_CODE_RenderingTemplate():
    def render(self) -> str:
        pass

@dataclass
class CPP_CODE_CppFunction(CPP_CODE_RenderingTemplate):
    states: list[CPP_CODE_RenderingTemplate] 
    global_statements: list[CPP_CODE_RenderingTemplate] 
    fsm_name: str
    cpp_auxiliary_functions: list[CPP_CODE_RenderingTemplate]
        
    def render(self) -> str:
        ret_val = ""
        
        for global_statement in self.global_statements:
            ret_val += "{}\n".format(global_statement.render())
        
        ret_val += "\n"
        ret_val += "{}\n".format(CPP_FSM_META_VARIABLE_DECLARATION(self.fsm_name))
        ret_val += "\n"
        ret_val += "{}\n".format(CPP_FUNCTION_HEADER(self.fsm_name))
        
        for state in self.states:
            ret_val += "{}\n".format(state.render())
        
        ret_val += "}\n\n"
        
        for aux_function in self.cpp_auxiliary_functions:
            ret_val += "{}\n".format(aux_function.render())
        
        return ret_val

@dataclass
class CPP_CODE_GlobalStatements(CPP_CODE_RenderingTemplate):
    statement: str
        
    def render(self) -> str:
        return self.statement
    
@dataclass
class CPP_CODE_States(CPP_CODE_RenderingTemplate):
    node_id: int
    code_block: list[str]
    entry_condition: str
    transitions: list[CPP_CODE_RenderingTemplate]
    fsm_name: str

    def render(self) -> str:
        ret_val = ""

        ret_val += "    {}\n".format(CPP_STATE_HEADER(self.fsm_name, self.node_id))
        
        if self.entry_condition != "":
            ret_val += "        {}\n\n".format(CPP_STATE_ENTRY_CONDITION(self.entry_condition))
            
        for code_line in self.code_block:
            ret_val += "        {}\n".format(code_line)
        
        ret_val += "\n"
        
        for transition in self.transitions:
            ret_val += "{}\n".format(transition.render())
        
        if len(self.transitions) == 0:
            ret_val += "        return;\n"
            
        ret_val += "    }\n"
        
        return ret_val
    
@dataclass 
class CPP_CODE_Transition(CPP_CODE_RenderingTemplate):
    condition: str
    code_block: list[str]
    target_node_id: int
    fsm_name: str
    
    def render(self) -> str:
        ret_val = ""
        if self.condition == "":
            for code_line in self.code_block:
                ret_val += "        {}\n".format(code_line)
                
            ret_val += "        {}\n".format(CPP_CHANGE_STATE(self.fsm_name, self.target_node_id))
            ret_val += "        return;\n"
        else:
            ret_val += "        {}\n".format(CPP_TRANSITION_HEADER(self.condition))
            for code_line in self.code_block:
                ret_val += "            {}\n".format(code_line)
                
            ret_val += "            {}\n".format(CPP_CHANGE_STATE(self.fsm_name, self.target_node_id))
            ret_val += "            return;\n"
            ret_val += "        }\n"
            
        return ret_val    

@dataclass
class CPP_CODE_CppFunction_EntryFixedIteration(CPP_CODE_RenderingTemplate):
    fsm_name: str
    
    def render(self) -> str:
        ret_val = ""
        
        ret_val += "{}\n".format(CPP_FUNCTION_FIXED_ITERATION_HEADER(self.fsm_name))
        ret_val += "    {}\n".format(CPP_FUNCTION_FIXED_ITERATION_LOOPS(self.fsm_name))
        
        ret_val += "}\n"
        
        return ret_val
    
@dataclass
class CPP_CODE_CppFunction_MinimumTimeIteration(CPP_CODE_RenderingTemplate):
    fsm_name: str
    
    def render(self) -> str:
        ret_val = ""
        
        ret_val += "{}\n".format(CPP_FUNCTION_MIN_TIME_DECLARE_TIME_VARIABLE(self.fsm_name))
        ret_val += "\n"
        ret_val += "{}\n".format(CPP_FUNCTION_MIN_TIME_ITERATION_HEADER(self.fsm_name))
        ret_val += "    {}\n".format(
            CPP_FUNCTION_MIN_TIME_REGISTER_TIME(self.fsm_name)
        )
        ret_val += "    {}\n".format(
            CPP_FUNCTION_MIN_TIME_ITERATION_LOOPS(
                CPP_FUNCTION_MIN_TIME_IS_TIME_PASSED(self.fsm_name, "ms")
            )
        )
        ret_val += "        {}();\n".format(self.fsm_name)
        ret_val += "    }\n"
        
        ret_val += "}\n"
        
        return ret_val