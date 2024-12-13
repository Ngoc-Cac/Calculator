import operator as opt, numpy as np

from copy import deepcopy

from mathparser import NVarMathFunction as NVF, SingleVarMathFunction as SVF,\
                       BinaryOperator, UnaryOperator, MathConstant, MathEvaluator,\
                       OperatorException, OperandException, NumericType, is_numeric

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import PyQt6.QtWidgets as Qtwidgets


import logging
logger = logging.getLogger('__main__.' + __name__)


def _factorial(num: float) -> int:
    if not num.is_integer():
        raise TypeError()
    else: num = int(num)
    result = 1
    for i in range(2, num + 1):
        result *= i
    return result

FACTORIAL = UnaryOperator('!', _factorial, 'left')

ADDITION = BinaryOperator('+', opt.add, 0, 'both')
SUBTRACTION = BinaryOperator('-', opt.sub, 0, 'both')
MULTIPLICATION = BinaryOperator('*', opt.mul, 1, 'both')
DIVISION = BinaryOperator('/', opt.truediv, 1, 'left')
EXPONENTIATION = BinaryOperator('^', opt.pow, 2, 'right')

SIN = SVF('sin', np.sin)
COS = SVF('cos', np.cos)
TAN = SVF('tan', np.tan)
COT = SVF('cot', lambda x: 1 / np.tan(x))

PI = MathConstant('pi', np.pi)
EULER = MathConstant('e', np.e)

OPERATORS: list[BinaryOperator] = [ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION,
                                   EXPONENTIATION, FACTORIAL]
FUNCTIONS: list[SVF] = [SIN, COS, TAN, COT]
CONSTANTS: list[MathConstant] = [PI, EULER]

my_eval = MathEvaluator(OPERATORS, FUNCTIONS, CONSTANTS, MULTIPLICATION.token)


def _evaluate(input: str) -> NumericType:
    result = my_eval.postfit_evaluate(my_eval.parse(input.lower()))
    return int(result) if result.is_integer() else result


class ErrorDialog(Qtwidgets.QDialog):
    def __init__(self, parent: Qtwidgets.QWidget, error_message: str) -> None:
        super().__init__(parent)
        self.setWindowTitle("Oh No! An error occured!")
        self.setFixedSize(300, 100)
        
        self.dialog_hbox = Qtwidgets.QHBoxLayout()
        self.dialog_vbox = Qtwidgets.QVBoxLayout()

        self.error_message = Qtwidgets.QLabel()
        self.error_message.setText(error_message)
        self.error_message.setWordWrap(True)
        self.error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.close_button = Qtwidgets.QPushButton()
        self.close_button.setText("Ok")
        self.close_button.clicked.connect(self.close)

        self.dialog_hbox.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dialog_vbox.addWidget(self.error_message)
        self.dialog_vbox.addLayout(self.dialog_hbox)
        self.setLayout(self.dialog_vbox)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

class InfoDialog(Qtwidgets.QDialog):
    def __init__(self, parent: Qtwidgets.QWidget, title: str, promt: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 100)
        
        self.dialog_hbox = Qtwidgets.QHBoxLayout()
        self.dialog_vbox = Qtwidgets.QVBoxLayout()

        self.promt = Qtwidgets.QLabel()
        self.promt.setText(promt)
        self.promt.setWordWrap(True)
        self.promt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.close_button = Qtwidgets.QPushButton()
        self.close_button.setText("Ok")
        self.close_button.clicked.connect(self.close)

        self.dialog_hbox.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dialog_vbox.addWidget(self.promt)
        self.dialog_vbox.addLayout(self.dialog_hbox)
        self.setLayout(self.dialog_vbox)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

class Home(Qtwidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.win_hbox = Qtwidgets.QHBoxLayout()
        self.win_vbox = Qtwidgets.QVBoxLayout()

        self.win_hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.win_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.win_hbox.addSpacing(10)

        self.input_box = self.init_input_box()
        self.result_label = self.init_result_label()

        self.win_hbox.addWidget(self.input_box)
        self.win_hbox.addWidget(self.result_label)
        self.win_vbox.addLayout(self.win_hbox)

        self.setLayout(self.win_vbox)
        
    def init_result_label(self) -> Qtwidgets.QLabel:
        result_font = QFont()
        result_font.setPointSize(18)
        result_font.setBold(True)
        result_label = Qtwidgets.QLabel()
        result_label.setFont(result_font)
        return result_label

    def init_input_box(self) -> Qtwidgets.QLineEdit:
        input_box = Qtwidgets.QLineEdit()
        input_box.setFixedSize(300, 30)
        input_box.returnPressed.connect(self.evaluate_input)
        return input_box

    def evaluate_input(self) -> None:
        user_input: str = self.input_box.text()
        error: bool = True

        logger.info(f"Input found: {user_input}")
        try:
            result = _evaluate(user_input)
            error = False
        except (OperatorException, OperandException) as e:
            error_message = ErrorDialog(self, str(e))
            error_message.show()
            logger.info("Input evaluated unsuccessfully due to wrong format")
        except Exception as e:
            logger.debug(e, exc_info=True)
            logger.error(f"Unexpected exception happend:\n{e}", exc_info=True)

        if error: result = ''
        else:
            if isinstance(result, float):
                result = f"{result: .9f}"
            else: result = str(result)
            self.input_box.clear()
            logger.info(f"Input evaluated successfully. Returning result: {result}")
        
        self.result_label.setText(result)

class Info(Qtwidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.info_vbox = Qtwidgets.QVBoxLayout()
        self.info_hbox = Qtwidgets.QHBoxLayout()

        self.init_instruction_text()


        self.info_hbox.addWidget(self.information_box, alignment=Qt.AlignmentFlag.AlignCenter)
        self.info_vbox.addLayout(self.info_hbox)

        self.setLayout(self.info_vbox)
    
    def init_instruction_text(self) -> None:
        self.information_box = Qtwidgets.QLabel()
        self.information_box.setText("not implemented yet, please do later")

class AddEdit(Qtwidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_layout()
        self.no_of_variables: int = 1
        self.dummy_variables: list[str] = [MathConstant(f'x_{i+1}', 0) for i in range(9)]
        self.func_eval = MathEvaluator(OPERATORS, FUNCTIONS, CONSTANTS + self.dummy_variables, MULTIPLICATION.token)
        

    def init_layout(self):
        self.edit_vbox = Qtwidgets.QVBoxLayout()
        self.edit_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.hbox_1 = Qtwidgets.QHBoxLayout()
        self.hbox_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hbox_2 = Qtwidgets.QHBoxLayout()
        self.hbox_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hbox_3 = Qtwidgets.QHBoxLayout()
        self.hbox_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hbox_4 = Qtwidgets.QHBoxLayout()
        self.hbox_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.titlefont = QFont()
        self.titlefont.setPointSize(15)
        self.contentfont = QFont()
        self.contentfont.setPointSize(10)

        self.addButton = Qtwidgets.QPushButton()

        self.init_hbox1()
        
        self.hbox_4.addWidget(self.addButton)

        self.edit_vbox.addLayout(self.hbox_1)
        self.edit_vbox.addLayout(self.hbox_2)
        self.edit_vbox.addLayout(self.hbox_3)
        self.edit_vbox.addLayout(self.hbox_4)

        self.setLayout(self.edit_vbox)

    def init_hbox1(self):
        self.combo_box = Qtwidgets.QComboBox()
        self.combo_box.addItems(['Constants', 'Functions'])
        self.combo_box.setFixedSize(150, 30)
        self.combo_box.setFont(self.titlefont)
        self.combo_box.currentTextChanged.connect(self.display_edit_ui)
        

        addlabel = Qtwidgets.QLabel()
        addlabel.setFont(self.titlefont)
        addlabel.setText('ADDING: ')


        self.hbox_1.addWidget(addlabel)
        self.hbox_1.addWidget(self.combo_box)

        self.display_edit_ui(self.combo_box.currentText())


    def display_edit_ui(self, string: str):
        self.clear_hbox(self.hbox_2)
        self.clear_hbox(self.hbox_3)
        try: self.addButton.clicked.disconnect()
        except TypeError: pass


        if string == 'Constants':
            self.add_constant_ui()
        else:
            self.add_function_ui()
    
    def clear_hbox(self, h_box: Qtwidgets.QHBoxLayout):
        for i in reversed(range(h_box.count())):
            h_box.itemAt(i).widget().setParent(None)
    
    
    def update_evaluator(self):
        for token, obj in my_eval.constants.items():
            if not token in self.func_eval.constants:
                self.func_eval.add_constant(obj)

        for token, obj in my_eval.functions.items():
            if not token in self.func_eval.functions:
                self.func_eval.add_function(obj)

        for token, obj in my_eval.operators.items():
            if not token in self.func_eval.operators:
                self.func_eval.add_operator(obj)

    def add_constant_ui(self):
        # note: limited to one character after underscore '_'
        def is_valid_name(name: str) -> bool:
            valid: bool = True
            temp = name.split('_')

            # Format checking
            if not temp[0].isalpha():
                error_message = ErrorDialog(self, "Invalid name {name}! Please choose another name!" if name
                                             else "No name was given for constant!")
                error_message.show()
                valid = False

            if len(temp) == 1:
                pass
            elif not (len(temp) == 2 and
                      len(temp[1]) == 1 and
                      temp[1].isalnum()
                     ):
                if valid:
                    error_message = ErrorDialog(self, f"Invalid name {name}! Please choose another name!")
                    error_message.show()
                valid = False
            
            # Uniqueness checking
            if name in my_eval.constants():
                error_message = ErrorDialog(self, f"Constant {name} already exists! Please choose another name!")
                error_message.show()
                valid = False

            return valid
        def evaluate_input(string_value: str) -> NumericType | None:
            error: bool = True
            
            logger.info(f"Input found: {string_value}")
            try:
                result = _evaluate(string_value)
                error = False
            except (OperatorException, OperandException) as e:
                error_message = ErrorDialog(self, str(e))
                error_message.show()
                logger.info("Value evaluated unsuccessfully due to wrong format")
            except Exception as e:
                logger.debug(e, exc_info=True)
                logger.error(f"Unexpected exception happend:\n{e}", exc_info=True)
            
            if error:
                return
            else:
                return result
        def add_constant():
            name_input: str = cons_name_input.text()
            value_input: str = cons_value_input.text()
            
            if not (
                    is_valid_name(name_input) and
                    (result := evaluate_input(value_input)) is None
                   ):
                return
            
            temp = MathConstant(name_input, result)
            my_eval.add_constant(temp)

            saved_info = InfoDialog(self, "Added Successfully!", f"New constant {name_input} has been added successfully!")
            saved_info.show()

            cons_name_input.clear()
            cons_value_input.clear()

        cons_name_input = Qtwidgets.QLineEdit()
        cons_name_input.setFixedSize(110, 30)
        cons_name_input.setFont(self.contentfont)

        cons_value_input = Qtwidgets.QLineEdit()
        cons_value_input.setFixedSize(600, 30)
        cons_value_input.setFont(self.contentfont)

        equal_sign = Qtwidgets.QLabel()
        equal_sign.setFont(self.contentfont)
        equal_sign.setText(' = ')
        

        self.hbox_2.addWidget(cons_name_input)
        self.hbox_2.addWidget(equal_sign)
        self.hbox_2.addWidget(cons_value_input)

        self.addButton.setText('Add Constant')
        self.addButton.setFont(self.titlefont)
        self.addButton.setFixedSize(150, 30)
        self.addButton.clicked.connect(add_constant)
    
    def add_function_ui(self):
        def update_label(label: Qtwidgets.QLabel):
            new_label = '(x_1'
            for i in range(1, self.no_of_variables):
                new_label += f', x_{i + 1}'
            new_label += ') = '

            label.setText(new_label)
        def update_dummy_var(add: bool = True):
            if add and self.no_of_variables < 9:
                self.no_of_variables += 1
                func_value_input.setFixedWidth(func_value_input.width() - 25)
                update_label(equal_sign)
            elif not add and self.no_of_variables > 1:
                self.no_of_variables -= 1
                func_value_input.setFixedWidth(func_value_input.width() + 25)
                update_label(equal_sign)

        def is_valid_name(name: str) -> bool:
            valid: bool = True
            temp = name.split('_')

            # Format checking
            if not temp[0].isalpha():
                error_message = ErrorDialog(self, "Invalid name {name}! Please choose another name!" if name
                                             else "No name was given for function!")
                error_message.show()
                valid = False

            if len(temp) == 1:
                pass
            elif not (len(temp) == 2 and
                      len(temp[1]) == 1 and
                      temp[1].isalnum()
                     ):
                if valid:
                    error_message = ErrorDialog(self, f"Invalid name {name}! Please choose another name!")
                    error_message.show()
                valid = False

            # Uniqueness checking
            if name in my_eval.functions:
                error_message = ErrorDialog(self, f"Function {name} already exists! Please choose another name!")
                error_message.show()
                valid = False

            return valid
        def proccess_expression(expr: str) -> list[str]:
            error: bool = False

            logger.info(f"Input found: {expr}")
            self.update_evaluator()

            try:
                result = self.func_eval.parse(expr)
            except (OperandException, ValueError) as e:
                error_message = ErrorDialog(self, str(e))
                error_message.show()
                error = True

            if not error:
                recognised_token = set(my_eval.operators) |\
                                   set(my_eval.functions) |\
                                   set(my_eval.constants)
                for string in result:
                    # check if this is a dummmy variable -> check if subscript of dummy variable exceeds no_of_var
                    if (
                        not (string in recognised_token or\
                             is_numeric(string)) and\
                        int(string[-1]) > self.no_of_variables
                       ):
                        error_message = ErrorDialog(self, f"Unrecognised token found {string}!\
                                                    Function only takes {self.no_of_variables} variables!")
                        error_message.show()
                        error = True

            return [] if error else result
        def add_function():
            name_input = func_name_input.text()
            expression = func_value_input.text()

            if not (is_valid_name(name_input) and
                    (expression := proccess_expression(expression))):
                return
            
            def func_operation(*args: NumericType, expression: list[str]) -> NumericType:
                for i, token in enumerate(expression):
                    if ''.join(token[:2]) == 'x_':
                        expression[i] = str(args[int(token[-1]) - 1])
                
                return my_eval.postfit_evaluate(expression)
            
            func_expr = deepcopy(expression)
            new_function = NVF(name_input, lambda *args: func_operation(*args, expression=func_expr),
                               self.no_of_variables)
            my_eval.add_function(new_function)

            saved_info = InfoDialog(self, "Added Successfully!", f"New function {name_input} has been added successfully!")
            saved_info.show()

            func_name_input.clear()
            func_value_input.clear()

        # UI and functionality stuff
        func_name_input = Qtwidgets.QLineEdit()
        func_name_input.setFixedSize(80, 30)
        func_name_input.setFont(self.contentfont)

        func_value_input = Qtwidgets.QLineEdit()
        func_value_input.setFixedSize(600, 30)
        func_value_input.setFont(self.contentfont)

        equal_sign = Qtwidgets.QLabel()
        equal_sign.setFont(self.contentfont)
        update_label(equal_sign)

        add_var_label = Qtwidgets.QLabel()
        add_var_label.setFont(self.contentfont)
        add_var_label.setText("Change number of variables: ")
        plus_button = Qtwidgets.QPushButton()
        minus_button = Qtwidgets.QPushButton()
        plus_button.setFont(self.titlefont)
        minus_button.setFont(self.titlefont)
        plus_button.setText('+')
        minus_button.setText('-')
        plus_button.setFixedSize(25,30)
        minus_button.setFixedSize(25,30)
        plus_button.clicked.connect(lambda: update_dummy_var(add=True))
        minus_button.clicked.connect(lambda: update_dummy_var(add=False))
        

        self.hbox_2.addWidget(func_name_input)
        self.hbox_2.addWidget(equal_sign)
        self.hbox_2.addWidget(func_value_input)

        self.hbox_3.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hbox_3.addWidget(add_var_label)
        self.hbox_3.addWidget(plus_button)
        self.hbox_3.addWidget(minus_button)

        self.addButton.setText('Add Function')
        self.addButton.setFont(self.titlefont)
        self.addButton.setFixedSize(150, 30)
        self.addButton.clicked.connect(add_function)


class Tabs(Qtwidgets.QTabWidget):
    def __init__(self, parent: Qtwidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.addTab(Info(), 'Help and Info')
        self.addTab(Home(), 'Home Tab')
        self.addTab(AddEdit(), 'Add and Edit')

class MainWindow(Qtwidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("My Calculator")
        self.setGeometry(450, 150, 770, 400)
        self.tabs = Tabs()
        self.tabs.setCurrentIndex(1)
        self.setCentralWidget(self.tabs)

def main_tasks():
    main_app = Qtwidgets.QApplication([])
    root_window = MainWindow()
    root_window.show()
    main_app.exec()


### Code testing section, please ignore

def test():
    main_tasks()
if __name__ == "__main__":
    test()