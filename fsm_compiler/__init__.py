from .parser import CHARACTERS
from .parser import parse_to_AST, generate_AST_from_code
from .assembler import generate_FSM_from_AST, optimize_FSM
from .code_gen import generate_code_from_FSM