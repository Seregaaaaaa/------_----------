class RPNInterpreter:
    def __init__(self):
        self.stack = []
        self.symbol_table = {}
        self.output = []
        self.instruction_pointer = 0
        self.input_values = []  # Входные данные из командной строки
        self.input_index = 0    # Индекс текущего входного значения
        
    def set_input_values(self, input_values):
        """Устанавливает входные данные для операций ввода"""
        self.input_values = input_values
        self.input_index = 0

    def interpret(self, rpn_instructions):
        self.stack = []
        self.symbol_table = {}  # Fresh symbol table for each run
        self.output = []
        self.instruction_pointer = 0
        self.input_index = 0  # Сбрасываем индекс входных данных для нового выполнения

        # print(f"Starting RPN interpretation: {rpn_instructions}")

        while self.instruction_pointer < len(rpn_instructions):
            instruction = rpn_instructions[self.instruction_pointer]
            # print(f"IP: {self.instruction_pointer}, Instr: {instruction}, Stack: {self.stack}, SymTable: {self.symbol_table}")

            if isinstance(instruction, (int, float)):  # Constants
                self.stack.append(instruction)
                self.instruction_pointer += 1
            elif isinstance(instruction, str):
                # Check if it's an identifier name pushed by the parser
                is_simple_identifier = (instruction.isidentifier() and
                                        instruction not in [
                                            "$JF", "$J", "ARR_INDEX", "OUTPUT_OP", "ASSIGN", "ASSIGN_ARR",
                                            "EQUALS", "MINUS", "PLUS", "MULTIPLY", "DIVIDE", "UNARY_MINUS",
                                            "LT", "GT", "NEQ", "AND", "OR", "DECL_ARR", "$r", "$w", "r_array", "ARRAY_INDEX", "ARRAY_ASSIGN"
                                        ])

                if is_simple_identifier:
                    self.stack.append(instruction) # Push identifier NAME
                    self.instruction_pointer += 1
                elif instruction == 'PLUS': # Изменено с '+'
                    self._binary_op(lambda a, b: a + b)
                    self.instruction_pointer += 1
                elif instruction == 'MINUS': # Изменено с '-'
                    self._binary_op(lambda a, b: a - b)
                    self.instruction_pointer += 1
                elif instruction == 'MULTIPLY': # Изменено с '*'
                    self._binary_op(lambda a, b: a * b)
                    self.instruction_pointer += 1
                elif instruction == 'DIVIDE': # Изменено с '/'
                    op2 = self._pop_operand()
                    op1 = self._pop_operand()
                    if op2 == 0:
                        raise ZeroDivisionError("Division by zero")
                    self.stack.append(op1 / op2)
                    self.instruction_pointer += 1
                elif instruction == 'UNARY_MINUS':
                    op = self._pop_operand()
                    self.stack.append(-op)
                    self.instruction_pointer += 1
                elif instruction == 'EQUALS':
                    self._binary_op(lambda a, b: int(a == b))
                    self.instruction_pointer += 1
                elif instruction == 'NEQ':
                    self._binary_op(lambda a, b: int(a != b))
                    self.instruction_pointer += 1
                elif instruction == 'LT': # Изменено с '<'
                    self._binary_op(lambda a, b: int(a < b))
                    self.instruction_pointer += 1
                elif instruction == 'GT': # Изменено с '>'
                    self._binary_op(lambda a, b: int(a > b))
                    self.instruction_pointer += 1
                elif instruction == 'AND': # Изменено с '&'
                    op2 = self._pop_operand()
                    op1 = self._pop_operand()
                    self.stack.append(int(bool(op1) and bool(op2)))
                    self.instruction_pointer += 1
                elif instruction == 'OR': # Изменено с '|'
                    op2 = self._pop_operand()
                    op1 = self._pop_operand()
                    self.stack.append(int(bool(op1) or bool(op2)))
                    self.instruction_pointer += 1
                elif instruction == "DECL_ARR":
                    # Stack: [..., size_val_or_name, array_name_str]
                    # Исправленный порядок: сначала извлекаем имя массива, потом размер
                    if not self.stack or not isinstance(self.stack[-1], str):
                        raise ValueError("DECL_ARR expected array name string on top of stack")
                    arr_name_str = self.stack.pop()  # Извлекаем имя массива

                    # Теперь извлекаем размер массива
                    if not self.stack:
                        raise ValueError("DECL_ARR expected size value on stack")
                    size_operand = self.stack.pop()
                    
                    # Получаем значение размера
                    if isinstance(size_operand, str):
                        if size_operand in self.symbol_table:
                            array_size = self.symbol_table[size_operand]
                        else:
                            raise NameError(f"Undefined variable: {size_operand}")
                    else:
                        array_size = size_operand
                    
                    # Проверяем размер
                    array_size = int(array_size)
                    if array_size <= 0:
                        raise ValueError(f"Array size must be positive, got {array_size}")
                    
                    # Создаем массив с нулевыми значениями указанного размера
                    self.symbol_table[arr_name_str] = [0] * array_size
                    self.instruction_pointer += 1
                
                elif instruction == "ASSIGN":
                    collected_rhs_values = []
                    while True:
                        if not self.stack:
                            raise ValueError("ASSIGN: Stack became empty while collecting RHS values.")
                        
                        potential_lhs = self.stack[-1]
                        is_lhs_candidate = False
                        if isinstance(potential_lhs, str) and \
                           potential_lhs.isidentifier() and \
                           not potential_lhs in ["$JF", "$J", "ARR_INDEX", "OUTPUT_OP", "ASSIGN", "ASSIGN_ARR",
                                               "EQUALS", "MINUS", "PLUS", "MULTIPLY", "DIVIDE", "UNARY_MINUS",
                                               "LT", "GT", "NEQ", "AND", "OR", "DECL_ARR", "$r", "$w", "r_array", "ARRAY_INDEX", "ARRAY_ASSIGN"]:
                            is_lhs_candidate = True
                        
                        if is_lhs_candidate:
                            # This is assumed to be the LHS. Stop collecting RHS.
                            break 
                        
                        collected_rhs_values.append(self._pop_operand())

                    if not self.stack: raise ValueError("ASSIGN: LHS name not found on stack.")
                    var_name = self.stack.pop() # This is the LHS name (string)

                    if not (isinstance(var_name, str) and var_name.isidentifier()):
                         raise ValueError(f"ASSIGN: Expected variable name (string), got {var_name}")

                    if len(collected_rhs_values) == 1:
                        self.symbol_table[var_name] = collected_rhs_values[0]
                    else:
                        # Array initialization, values were collected in reverse order of appearance in {}
                        self.symbol_table[var_name] = list(reversed(collected_rhs_values))
                    self.instruction_pointer += 1
                
                elif instruction == "ARR_INDEX":
                    # Stack: [..., array_name_str, index_val_or_name]
                    index_val = self._pop_operand() # Resolves index if it's a name
                    
                    if not self.stack or not isinstance(self.stack[-1], str):
                        raise ValueError("ARR_INDEX expected array name string on stack")
                    arr_name_str = self.stack.pop() 

                    if arr_name_str not in self.symbol_table:
                        raise NameError(f"Array '{arr_name_str}' not defined.")
                    array_obj = self.symbol_table[arr_name_str]
                    if not isinstance(array_obj, list):
                        raise TypeError(f"'{arr_name_str}' is not an array.")
                    
                    self.stack.append(array_obj[int(index_val)])
                    self.instruction_pointer += 1
                
                elif instruction == "ASSIGN_ARR":
                    # Stack: [..., array_name_str, index_val_or_name, value_val_or_name]
                    value_to_assign = self._pop_operand()
                    index = self._pop_operand()
                    
                    if not self.stack or not isinstance(self.stack[-1], str):
                        raise ValueError("ASSIGN_ARR expected array name string on stack")
                    arr_name_str = self.stack.pop()

                    if arr_name_str not in self.symbol_table:
                         raise NameError(f"Array '{arr_name_str}' not defined or not initialized as an array.")
                    
                    array_obj = self.symbol_table[arr_name_str]
                    if not isinstance(array_obj, list):
                        raise TypeError(f"'{arr_name_str}' is not an array for ASSIGN_ARR.")

                    idx_int = int(index)
                    if idx_int < 0 :
                         raise IndexError(f"Array index {idx_int} out of bounds for array '{arr_name_str}'.")
                    
                    # Ensure array is large enough, extend if necessary (Pythonic) or error (C-like)
                    # For now, let's assume C-like fixed size after initialization.
                    if idx_int >= len(array_obj):
                        raise IndexError(f"Array index {idx_int} out of bounds for array '{arr_name_str}' of size {len(array_obj)}.")
                    
                    array_obj[idx_int] = value_to_assign
                    self.instruction_pointer += 1
                
                elif instruction == "$JF":
                    target_address_idx = rpn_instructions[self.instruction_pointer + 1]
                    if not isinstance(target_address_idx, int):
                        raise TypeError(f"$JF target address must be an int, got {target_address_idx}")
                    condition_result = self._pop_operand()
                    if not condition_result:  # False if 0
                        self.instruction_pointer = target_address_idx
                    else:
                        self.instruction_pointer += 2
                
                elif instruction == "$J":
                    target_address_idx = rpn_instructions[self.instruction_pointer + 1]
                    if not isinstance(target_address_idx, int):
                        raise TypeError(f"$J target address must be an int, got {target_address_idx}")
                    self.instruction_pointer = target_address_idx
                
                elif instruction == "OUTPUT_OP":
                    value_to_output = self._pop_operand()
                    self.output.append(value_to_output)
                    # print(f"OUTPUT: {value_to_output}")
                    self.instruction_pointer += 1
                
                elif instruction == "$r":
                    # Операция ввода - читает значение и присваивает переменной
                    if not self.stack:
                        raise ValueError("INPUT operation expected variable name on stack")
                    var_name = self.stack.pop()  # Получаем имя переменной как строку
                    if not isinstance(var_name, str):
                        raise TypeError(f"INPUT operation expected variable name (string), got {var_name}")
                    
                    # Интерактивный ввод
                    try:
                        input_value = int(input(f"Введите значение для переменной '{var_name}': "))
                    except ValueError:
                        print("Ошибка: введите целое число.")
                        input_value = 0
                    except EOFError:
                        # Если ввод недоступен (например, в тестах), используем значения по умолчанию
                        if hasattr(self, 'input_values') and self.input_values and self.input_index < len(self.input_values):
                            input_value = self.input_values[self.input_index]
                            self.input_index += 1
                        else:
                            input_value = 0
                    
                    self.symbol_table[var_name] = input_value
                    self.instruction_pointer += 1
                
                elif instruction == "$w":
                    # Операция вывода - выводит значение с вершины стека
                    value_to_output = self._pop_operand()
                    self.output.append(value_to_output)
                    self.instruction_pointer += 1
                
                elif instruction == "r_array":
                    # Операция ввода в массив: input arr[index]
                    # Стек: [array_name, index_value]
                    index_value = self._pop_operand()
                    
                    if not self.stack or not isinstance(self.stack[-1], str):
                        raise ValueError("r_array operation expected array name on stack")
                    array_name = self.stack.pop()
                    
                    # Интерактивный ввод для массива
                    try:
                        input_value = int(input(f"Введите значение для элемента {array_name}[{index_value}]: "))
                    except ValueError:
                        print("Ошибка: введите целое число.")
                        input_value = 0
                    except EOFError:
                        # Если ввод недоступен (например, в тестах), используем значения по умолчанию
                        if hasattr(self, 'input_values') and self.input_values and self.input_index < len(self.input_values):
                            input_value = self.input_values[self.input_index]
                            self.input_index += 1
                        else:
                            input_value = 0
                    
                    # Присваиваем значение элементу массива
                    if array_name not in self.symbol_table:
                        raise NameError(f"Array '{array_name}' not defined")
                    array_obj = self.symbol_table[array_name]
                    if not isinstance(array_obj, list):
                        raise TypeError(f"'{array_name}' is not an array")
                    
                    idx = int(index_value)
                    if idx < 0 or idx >= len(array_obj):
                        raise IndexError(f"Array index {idx} out of bounds for array '{array_name}'")
                    
                    array_obj[idx] = input_value
                    self.instruction_pointer += 1
                
                elif instruction == "ARRAY_INDEX":
                    # Операция доступа к элементу массива: arr[index]
                    # Стек: [array_name, index_value]
                    index_value = self._pop_operand()
                    
                    if not self.stack or not isinstance(self.stack[-1], str):
                        raise ValueError("ARRAY_INDEX operation expected array name on stack")
                    array_name = self.stack.pop()
                    
                    # Получаем значение элемента массива
                    if array_name not in self.symbol_table:
                        raise NameError(f"Array '{array_name}' not defined")
                    array_obj = self.symbol_table[array_name]
                    if not isinstance(array_obj, list):
                        raise TypeError(f"'{array_name}' is not an array")
                    
                    idx = int(index_value)
                    if idx < 0 or idx >= len(array_obj):
                        raise IndexError(f"Array index {idx} out of bounds for array '{array_name}'")
                    
                    # Помещаем значение элемента массива на стек
                    self.stack.append(array_obj[idx])
                    self.instruction_pointer += 1
                
                elif instruction == "ARRAY_ASSIGN":
                    # Операция присваивания элементу массива: arr[index] = value
                    # Стек: [array_name, index_value, value_to_assign]
                    value_to_assign = self._pop_operand()
                    index_value = self._pop_operand()
                    
                    if not self.stack or not isinstance(self.stack[-1], str):
                        raise ValueError("ARRAY_ASSIGN operation expected array name on stack")
                    array_name = self.stack.pop()
                    
                    # Присваиваем значение элементу массива
                    if array_name not in self.symbol_table:
                        raise NameError(f"Array '{array_name}' not defined")
                    array_obj = self.symbol_table[array_name]
                    if not isinstance(array_obj, list):
                        raise TypeError(f"'{array_name}' is not an array")
                    
                    idx = int(index_value)
                    if idx < 0 or idx >= len(array_obj):
                        raise IndexError(f"Array index {idx} out of bounds for array '{array_name}'")
                    
                    array_obj[idx] = value_to_assign
                    self.instruction_pointer += 1
                
                else:
                    raise ValueError(f"Unknown string RPN instruction: {instruction}")
            else:
                raise TypeError(f"Unknown RPN instruction type: {instruction} ({type(instruction)})")
        
        # print(f"Final Stack: {self.stack}")
        # print(f"Final Symbol Table: {self.symbol_table}")
        # print(f"Final Output: {self.output}")
        return self.output, self.symbol_table

    def _pop_operand(self):
        if not self.stack:
            raise IndexError("Stack underflow: trying to pop operand")
        operand = self.stack.pop()
        if isinstance(operand, str): 
            if operand in self.symbol_table:
                return self.symbol_table[operand]
            else:
                # Проверяем, что это не название операции
                operations = ["$JF", "$J", "ARR_INDEX", "OUTPUT_OP", "ASSIGN", "ASSIGN_ARR",
                             "EQUALS", "MINUS", "PLUS", "MULTIPLY", "DIVIDE", "UNARY_MINUS",
                             "LT", "GT", "NEQ", "AND", "OR", "DECL_ARR", "$r", "$w", "r_array", "ARRAY_INDEX", "ARRAY_ASSIGN"]
                if operand in operations:
                    raise ValueError(f"Tried to pop operation '{operand}' as operand")
                
                # Для неопределенных переменных возвращаем 0 (автоинициализация)
                self.symbol_table[operand] = 0
                return 0
        return operand

    def _binary_op(self, op_func):
        op2 = self._pop_operand()
        op1 = self._pop_operand()
        self.stack.append(op_func(op1, op2))

