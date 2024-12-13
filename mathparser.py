"""
Involves defining math operators, functions, parsing tokens
and evaluating expressions relating to mentioned operators and functions.
"""

from copy import deepcopy
from enum import Enum
from typing import Literal, Callable, Optional, Union, TypeAlias, Iterable

# Type Annotation Stuff
NumericType: TypeAlias = Union[int, float]
SingleVarFunctionType: TypeAlias = Callable[[NumericType], NumericType]
NVarFunctionType = Callable[[*list[NumericType]], NumericType]

class OperatorException(Exception):
    """
    Exception throws when:
        - Operator token does not exist
        - Operation is not defined
    """

class OperandException(Exception):
    """
    Exception throws when:
        - Operand is not numeric.
        - There is too much or too little operands to work with.
        - Mismatched parenthesis in expression.
    """


class Associativity(Enum):
    """
    Associativity of operators represent the direction of which\
    to apply the operator.

    #### For binary operators:
        Left-associative operators must be applied from left to right,\
            right-associative opertors must be applied from right to left.
        'SPECIAL' means that the operator is left AND right associative\
            and may be apply in any direction.
    #### For unary operators:
        Left-associative operators apply to the numeric value to the left of it.\
            Right-associative operator apply to the numeric value ot the right of it.
        No unary operator can have 'SPECIAL' associativity.

    For example:
        - '!' as factorial over integer is right-associative. As a result, '2!'\
            is a meaningful expression, whereas '!2' is not.
        - '-' as division over real number may be defined as left\
            associative. As a result, '3-2-1' is '(3-2)-1' which is '0'.
        - '^' as exponentiation over real number may be defined as right\
            associative. As a result, '2^2^3' is '2^(2^3)' which is '2^8'.
        - '+' as addition over real number is both left and right associative\
            in any interpretation. As a result, '1+2+3' is '1+(2+3)' or '(1+2)+3',\
            resulting in '6'.
    """
    RIGHT = 0
    LEFT = 1
    SPECIAL = 2

class NVarMathFunction():
    """
    This class represents a n-variable function. This class is also a Callable that
    takes n numeric values and return a numeric value.

    ---
    ## Attributes:
        operation: A Callable representing the action to do when applying the function to\
            n_var numeric values.
        token: the string that represent the function.
        n_var: the number of variables that the function takes.
    """
    __slots__ = '_token', '_operation', '_n_var'
    _token: str
    _operation: NVarFunctionType
    _n_var: int

    def __init__(self, token: str, operation: NVarFunctionType, n_var: int) -> None:
        """
        Initalise a N-variable function.

        ---
        ## Parameters:
        token: a string representing the operator.
        operation: a function that takes n_var numerics and return one numeric.
        n_var: the number of variables that the function takes, must be at least 2.
        """
        if not isinstance(token, str):
            raise TypeError("Character representation must be of type string!")
        elif not token:
            raise ValueError("Character representation must not be empty!")
        if not isinstance(n_var, int):
            raise TypeError("Number of variables must be an integer!")
        elif n_var < 1:
            raise ValueError("Number of variables for a n-variable function must be at least 1!")
        if not isinstance(operation, Callable):
            raise TypeError(f"Operation must be a function that takes {n_var} numbers and returns a number!")
        
        self._token = token
        self._operation = operation
        self._n_var = n_var
    

    @property
    def token(self) -> str:
        """String representation of function"""
        return self._token
    @token.setter
    def token(self, new_token: str) -> None:
        if not isinstance(new_token, str):
            raise TypeError("Character representation must be of type string!")
        elif not new_token:
            raise ValueError("Character representation must not be empty!")
        self._token = new_token

    @property
    def operation(self) -> NVarFunctionType:
        """The operation of the function. This should take in n-var amounts of numbers
        and output one number"""
        return deepcopy(self._operation)
    @operation.setter
    def operation(self, new_operation: NVarFunctionType) -> None:
        if not isinstance(new_operation, Callable):
            raise TypeError(f"Operation must be a function that takes {self.n_var} numbers and returns a number!")
        self._operation = new_operation
    
    @property
    def n_var(self) -> int:
        """Number of variables the function can take"""
        return self._n_var
    @n_var.setter
    def n_var(self, n_var: int) -> None:
        if not isinstance(n_var, int):
            raise TypeError("Number of variables must be an integer!")
        elif n_var < 1:
            raise ValueError("Number of variables for a n-variable function must be at least 1!")
        self._n_var = n_var

    def __call__(self, *args: NumericType) -> NumericType:
        if len(args) != self.n_var:
            raise OperandException(f"Too many inputs given, expected {self.n_var} inputs")
        return self._operation(*args)

class SingleVarMathFunction(NVarMathFunction):
    """
    This class represents a single-variable function. This class is also a Callable that
    takes a numeric value and return a numeric value.

    ---
    ## Attributes:
        operation:A Callable representing the action to do when applying the function to\
            a numeric value.
        token: the string that represent the function.
    """
    def __init__(self, token: str, operation: SingleVarFunctionType) -> None:
        """
        Intialise a single-var function.

        ---
        ## Attribute:
            token: a string representing the function. For example: 'sin'\
                is defined as the trigonometric sine function.
            operation: a function that takes a numeric value and return a\
                numeric value.
        """
        super().__init__(token, operation, 1)
    
    @NVarMathFunction.n_var.setter
    def n_var(self, n_var: int) -> None:
        raise AttributeError("Cannot set n_var for single-variable function!")

    # def __call__(self, x: NumericType) -> NumericType:
    #     """
    #     Evaluate the result with the given operation.
    #     """
    #     return self._operation(x)

class UnaryOperator(SingleVarMathFunction):
    __slots__ = '_associativity'
    _associativity: Associativity

    def __init__(self, token: str, operation: SingleVarFunctionType,
                       associativity: Literal['left', 'right']) -> None:
        self.associativity = associativity
        super().__init__(token, operation)
    

    @property
    def associativity(self) -> Associativity:
        return self._associativity
    @associativity.setter
    def associativity(self, new_associativity: Literal['left', 'right']) -> None:
        if new_associativity == 'left':
            self._associativity = Associativity.LEFT
        elif new_associativity == 'right':
            self._associativity = Associativity.RIGHT
        else:
            raise TypeError("Associativity must be a string literal of 'left' or 'right'")

class BinaryOperator(NVarMathFunction):
    """
    This class represents a binary operator. This class is also a Callable that takes
    two numeric values and return a numeric value.
    
    ---
    ## Attributes:
        associativity: the associativity of the operator.
        operation: A Callable representing the action to do when applying the operator\
            on two numeric values. This function should take in some numbers and out\
            put one number.
        precedence: the priority of the operator.
        token: the string that represent the operator.
    """
    __slots__ = '_precedence', '_associativity'
    _precedence: int
    _associativity: Associativity

    def __init__(self, token: str, operation: NVarFunctionType, precedence: int,
                       associativity: Literal['left', 'right', 'both']) -> None:
        """
        Initalise a Binary Operator.

        ---
        ## Parameters:
        token: a string, preferably a single character, representing the operator.
        operation: a function that takes two numerics and return one numeric.
        precedence: an integer that determines the priority of the operator.\
            Operator with higher precedence has higher priority.
        associativity: a string representing the associativity of an operator.\
            For more information, refer to Associativity Enum.
        """
        self.associativity = associativity
        self.precedence = precedence
        super().__init__(token, operation, n_var=2)
  
    
    @property
    def precedence(self) -> int:
        """The precedence of operator."""
        return self._precedence
    @precedence.setter
    def precedence(self, new_precedence: int) -> None:
        if not isinstance(new_precedence, int):
            raise TypeError("Precedence of operator must be an integer!")
        self._precedence = new_precedence
    
    @property
    def associativity(self) -> int:
        """The associativity of operator. Refer to Associativity Enum for more information"""
        return self._associativity
    @associativity.setter
    def associativity(self, new_associativity: Literal['left', 'right', 'both']) -> None:
        if new_associativity == 'left':
            self._associativity = Associativity.LEFT
        elif new_associativity == 'right':
            self._associativity = Associativity.RIGHT
        elif new_associativity == 'both':
            self._associativity = Associativity.SPECIAL
        else:
            raise TypeError("Associativity must be a string literal of 'left', 'right' or 'both'")
    
    @NVarMathFunction.n_var.setter
    def n_var(self, n_var: int) -> None:
        raise OperandException("Cannot set n_var for binary operators!")

class MathConstant():
    """
    This class represents a constant, a symbol that has a numeric value.

    ---
    ## Attributes:
        token: the string that represent the constant.
        value: the numeric value of the constant.
    """
    __slots__ = '_token', '_value'
    def __init__(self, token: str, value: NumericType) -> None:
        """
        Intialise a constant.

        ---
        ## Attribute:
            token: a string representing the constant.
            value: the numeric value of the constant.
        """
        if not isinstance(token, str):
            raise TypeError("Character representation of constant must be a non-empty string!")
        elif not token:
            raise ValueError("Character representation of constant must not be an empty string!")
        if not isinstance(value, NumericType):
            raise TypeError("Value of constant must be numerical")
        
        self._token = token
        self._value = value

    @property
    def token(self) -> str:
        """String representation of constant"""
        return self._token
    @token.setter
    def token(self, new_token: str) -> None:
        if not isinstance(new_token, str):
            raise TypeError("Character representation of constant must be a non-empty string!")
        elif not new_token:
            raise ValueError("Character representation of constant must not be an empty string!")
        self._token = new_token
    
    @property
    def value(self) -> NumericType:
        """The numeric value of constant."""
        return self._value
    @value.setter
    def value(self, new_value: NumericType):
        if not isinstance(new_value, NumericType):
            raise TypeError("Value of constant must be numerical")
        self._value = new_value


Operator: TypeAlias = Union[UnaryOperator, BinaryOperator]
class MathEvaluator():
    __slots__ = '_operators', '_functions', '_constants', '_implicit_operation'
    _operators: dict[str, Operator]
    _functions: dict[str, NVarMathFunction]
    _constants: dict[str, MathConstant]
    _implicit_operation: Optional[BinaryOperator]

    def __init__(self, operators: Iterable[Operator] = [],
                       functions: Iterable[NVarMathFunction] = [],
                       constants: Iterable[MathConstant] = [],
                       implicit_operation_token: str = '') -> None:
        if not isinstance(operators, Iterable):
            raise TypeError("Operators must be a list of Unary/Binary Operator!")
        if not isinstance(functions, Iterable):
            raise TypeError("Functions must be a list of single-var/n-var Math Function!")
        if not isinstance(constants, Iterable):
            raise TypeError("Constants must be a list of Math Constants!")
        if not isinstance(implicit_operation_token, str):
            raise TypeError("Token of implicit operation must be a string!")
        self._operators = {}
        self._functions = {}
        self._constants = {}
        for operator in operators:
            self.add_operator(operator)
        for func in functions:
            self.add_function(func)
        for const in constants:
            self.add_constant(const)

        if implicit_operation_token in self._operators:
            self._implicit_operation = self._operators[implicit_operation_token]
        else:
            self._implicit_operation = None

    @property
    def operators(self) -> dict[str, Operator]:
        return deepcopy(self._operators)
    def add_operator(self, operator: Operator) -> None:
        if not isinstance(operator, Operator):
            raise TypeError("Operator must be a unary/binary operator!")
        elif operator.token in self._operators:
            raise ValueError(f"Operator token '{operator.token}' already exists!")
        self._operators[operator.token] = operator
    
    @property
    def functions(self) -> dict[str, NVarMathFunction]:
        return deepcopy(self._functions)
    def add_function(self, func: NVarMathFunction) -> None:
        if not isinstance(func, NVarMathFunction):
            raise TypeError("func must be a single-var/muli-var function!")
        elif func.token in self._operators:
            raise ValueError(f"Function token '{func.token}' already exists!")
        self._functions[func.token] = func

    @property
    def constants(self) -> dict[str, MathConstant]:
        return deepcopy(self._constants)
    def add_constant(self, constant: MathConstant) -> None:
        if not isinstance(constant, MathConstant):
            raise TypeError("Constant must be a Math Constant!")
        elif constant.token in self._constants:
            raise ValueError(f"Constant token '{constant.token}' already exists!")
        self._constants[constant.token] = constant

    @property
    def implicit_operation(self) -> BinaryOperator:
        return deepcopy(self._implicit_operation)
    @implicit_operation.setter
    def implicit_operation(self, implicit_operation_token: str) -> None:
        if implicit_operation_token in self._operators:
            self._implicit_operation = self._operators[implicit_operation_token]
        else:
            raise OperatorException(f"Token of binary operator does not exist '{implicit_operation_token}'")

    def parse(self, expr: str) -> list[str]:
        substr: list[str] = self._shuntyard_format_string(expr)
        opt_stack: list[str] = []
        val_stack: list[str] = []

        def check_implicit_operation(index: int) -> None:
            """
            Check for implicit operation.\n
            Implicit operations are implied operation between a numeric value and\
                a function/constant.\n
            For example: if '*' is an implicit_operation and 'pi' is a constant,\
                then there is a hidden '*' between 2 and 'pi' in '2pi' -> '2*pi'.\
                This is parsed as '2 pi *' in RPN.
            """
            if (
                index != 0 and \
                is_numeric(substr[index-1]) and\
                self._implicit_operation
            ):
                opt_stack.append(self._implicit_operation.token)
        def operator_condition(operator_1: Operator,
                               operator_2: Operator) -> bool:
            """
            Condition checking for shunting yard algorithm when token is an operator
            """
            if (op1_is_unary := isinstance(operator_1, UnaryOperator)) or\
               (op2_is_unary := isinstance(operator_2, UnaryOperator)):
                return (not op1_is_unary) and op2_is_unary
            
            lower_precedence: bool = operator_1.precedence < operator_2.precedence
            left_associative: bool = operator_1.precedence == operator_2.precedence and\
                                        (operator_1.associativity == Associativity.LEFT or\
                                         operator_1.associativity == Associativity.SPECIAL)
            return lower_precedence or left_associative
        

        for i, string in enumerate(substr):
            if is_numeric(string):
                val_stack.append(string)
            elif string in self._constants:
                check_implicit_operation(i)
                val_stack.append(string)
            elif string in self._functions:
                check_implicit_operation(i)
                opt_stack.append(string)
            elif string in self._operators:
                while (
                    len(opt_stack) != 0 and opt_stack[-1] != '(' and\
                    operator_condition(self._operators[string],
                                       self._operators[opt_stack[-1]])
                ):
                    val_stack.append(opt_stack.pop())
                opt_stack.append(string)
            elif string == ',':
                if len(opt_stack) == 0:
                    raise OperandException("Mismatched parenthesis for '('")
                while opt_stack[-1] != '(':
                    val_stack.append(opt_stack.pop())
                    if len(opt_stack) == 0:
                        raise OperandException("Mismatched parenthesis for '('")
            elif string == '(':
                opt_stack.append(string)
            elif string == ')':
                if len(opt_stack) == 0:
                    raise OperandException("Mismatched parenthesis for ')'")
                while opt_stack[-1] != '(':
                    val_stack.append(opt_stack.pop())
                    if len(opt_stack) == 0:
                        raise OperandException("Mismatched parenthesis for ')'")
                opt_stack.pop()
                if len(opt_stack) != 0 and opt_stack[-1] in self._functions:
                    val_stack.append(opt_stack.pop())
            else:
                raise ValueError(f"Unrecognised token, has not been implemented yet \"{string}\"")
            
        while opt_stack:
            if opt_stack[-1] == '(':
                raise OperandException("Mismatched parenthesis for '('")
            val_stack.append(opt_stack.pop())

        return val_stack

    def postfit_evaluate(self, expr: list[str]) -> NumericType:
        if not isinstance(expr, list):
            raise TypeError("Expecting a list of strings!")
        elif not expr:
            return 0
        values: list[NumericType] = []

        for char in expr:
            if ((opt_found := char in self._operators) or\
                char in self._functions):
                temp = []
                refer = self._operators[char] if opt_found else self._functions[char]
                try:
                    for _ in range(refer.n_var):
                        temp.append(values.pop())
                except IndexError:
                    raise OperandException(f"Too few operands to evaluate '{char}'")
                temp.reverse()
                values.append(refer(*temp))
            else:
                if char in self._constants:
                    char = self._constants[char].value
                else:
                    try:
                        char = float(char)
                    except ValueError:
                        raise OperandException(f"Non-numeric value was given: '{char}'")
                values.append(char)

        if len(values) != 1:
            raise OperandException("Too many operands was given")
        return values.pop()

    def _shuntyard_format_string(self, string: str) -> list[str]:
        """
        Format string expression for Shunting-Yard parsing algorithm.\n
        The result should be a list of strings, where each element is\
            a number or an existing token.\n
        For example, passing 'cos(pi + 2) -3' will produce the list:\n
            ['cos', '(', 'pi', '+', '2', ')', '-', '3']
        """
        recognised_tokens: set[str] = set(self._operators) |\
                                      set(self._functions) |\
                                      set(self._constants)
        output: list[str] = []


        for token in recognised_tokens:
            if token in string:
                temp = string.split(token)
                string = f" {token} ".join(temp)

        for sub in string.split():
            if sub in recognised_tokens or\
               is_numeric(sub):
                output.append(sub)
            else:
                output.extend(sub)

        return output
    

# Utility methods
def is_numeric(string: str) -> bool:
    try:
        float(string)
    except (ValueError, TypeError):
        return False
    return True


### Testing Zone ###

def test():
    import operator as opt
    addition = BinaryOperator('+', opt.add, 0, 'both')
    subtraction = BinaryOperator('-', opt.sub, 0, 'both')
    multiplication = BinaryOperator('*', opt.mul, 1, 'both')
    division = BinaryOperator('/', opt.truediv, 1, 'left')
    my_eval = MathEvaluator()
    for oper in [addition, subtraction, multiplication, division]:
        my_eval.add_operator(oper)
    print(my_eval.parse("-3"))

if __name__ == "__main__":
    test()