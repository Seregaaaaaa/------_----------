class RPNGenerator:

    def __init__(self):
        self.rpn = []  
        self.current_index = 0  
        self.operator_stack = []  # Добавляем стек для операторов
        
        # Задаем приоритеты операторов
        self.operator_precedence = {
            '+': 1,
            '-': 1, 
            '*': 2,
            '/': 2,
            '~': 3,  # унарный минус имеет высокий приоритет
            '<': 0,
            '>': 0,
            '?': 0,  # сравнения на равенство (==)
            '!': 0,  # сравнения на неравенство (!=)
            '&': -1, # логическое И
            '|': -2, # логическое ИЛИ
            '=': -3  # присваивание имеет самый низкий приоритет
        }
        
    def add_identifier(self, name):
        """
        Добавляет идентификатор переменной в ОПС
        a <идентификатор> -> <идентификатор переменной>
        """
        self.rpn.append(name)
        self.current_index += 1
        
    def add_constant(self, value_str): # value_str - это строка из лексера, например, "10" или "3.14"
        """
        Добавляет константу в ОПС.
        Преобразует строковое значение в числовой тип (int или float).
        Если преобразование не удается, вызывает ValueError, так как это указывает
        на проблему с токеном константы, полученным от лексера.
        """
        processed_value = None
        try:
            # Сначала пытаемся преобразовать в int
            processed_value = int(value_str)
        except ValueError:
            # Если не получилось в int (например, для "3.14"), пытаемся в float
            try:
                processed_value = float(value_str)
            except ValueError:
                # Если оба преобразования не удались, это критическая ошибка.
                # Лексер должен предоставлять корректные числовые строки для констант.
                raise ValueError(
                    f"RPNGenerator: Критическая ошибка. Не удалось преобразовать значение токена '{value_str}' "
                    f"(ожидалось число) в int или float. "
                    f"Возможно, лексер создал некорректный токен константы."
                )

        self.rpn.append(processed_value)
        self.current_index += 1
        # print(f"DEBUG: RPNGenerator добавил константу {processed_value} (тип: {type(processed_value)})")
        
    def get_precedence(self, operator):
        """Возвращает приоритет оператора"""
        return self.operator_precedence.get(operator, 0)
        
    def push_to_operator_stack(self, operator):
        """Добавляет оператор в стек операторов с учетом приоритетов"""
        
        if operator == "(":
            # Открывающая скобка всегда добавляется в стек
            self.operator_stack.append(operator)
        else:
            # Для других операторов применяем правила приоритета
            while (self.operator_stack and operator != "(" and 
                   self.operator_stack[-1] != "(" and 
                   self.get_precedence(self.operator_stack[-1]) >= self.get_precedence(operator)):
                # Извлекаем операторы с большим или равным приоритетом
                top_operator = self.operator_stack.pop()
                self.add_operator(top_operator)
            
            # Добавляем текущий оператор в стек
            self.operator_stack.append(operator)
            
    def pop_operator_stack_until(self, delimiter):
        """
        Извлекает операторы из стека операторов до указанного разделителя и добавляет их в ОПС
        Если разделитель - пустая строка, извлекаются все операторы из стека
        """
        if delimiter == "":
            # Извлекаем все операторы из стека
            while self.operator_stack:
                operator = self.operator_stack.pop()
                self.add_operator(operator)
        else:
            # Извлекаем операторы до указанного разделителя
            while self.operator_stack and self.operator_stack[-1] != delimiter:
                operator = self.operator_stack.pop()
                self.add_operator(operator)
                
            if self.operator_stack and self.operator_stack[-1] == delimiter:
                self.operator_stack.pop()  # Удаляем разделитель
        
    def add_operator(self, operator):
        """Добавляет оператор в ОПС"""
        operator_map = {
            '+': "PLUS",
            '-': "MINUS",
            '*': "MULTIPLY",
            '/': "DIVIDE",
            '<': "LT",
            '>': "GT",
            '!': "NEQ",
            '?': "EQUALS",
            '&': "AND",
            '|': "OR",
            '~': "UNARY_MINUS",
            '=': "ASSIGN",
            'w': "$w",
            'r': "$r",
            'r_array': "r_array",
            'i': "$i", 
            'init': "LIST",
            'GEN': "$GEN", 
            'DECL_ARR': "DECL_ARR",
            'comma': "COMMA",
            'array_index': "ARRAY_INDEX",
            'array_assign': "ARRAY_ASSIGN",
            '$JF': "$JF",
            '$J': "$J",
        }
        
        if operator in operator_map:
            self.rpn.append(operator_map[operator])
            self.current_index += 1
        else:
            raise ValueError(f"Неизвестный оператор: {operator}")
        


    def add_conditional_jump(self): # Убираем аргумент label
        """Добавляет условный переход $JF с заполнителем и возвращает индекс заполнителя."""
        self.rpn.append("$JF")
        self.current_index += 1
        placeholder_index = self.current_index # Индекс, где будет стоять адрес
        self.rpn.append("_")  # Заполнитель для адреса
        self.current_index += 1
        return placeholder_index

    def add_unconditional_jump_placeholder(self):
        """Добавляет безусловный переход $J с заполнителем и возвращает индекс заполнителя."""
        self.rpn.append("$J")
        self.current_index += 1
        placeholder_index = self.current_index # Индекс, где будет стоять адрес
        self.rpn.append("_")  # Заполнитель для адреса
        self.current_index += 1
        return placeholder_index

    def patch_jump_address(self, rpn_placeholder_index, target_address):
        """Заменяет заполнитель адреса перехода по указанному индексу в ОПС."""
        if 0 <= rpn_placeholder_index < len(self.rpn) and self.rpn[rpn_placeholder_index-1] in ["$JF", "$J"]:
            # Убедимся, что target_address является числом
            self.rpn[rpn_placeholder_index] = int(target_address)
        else:
            # Можно добавить логирование ошибки, если индекс некорректен
            pass

    def add_jump_to_known_target(self, target_label):
        """Добавляет безусловный переход $J на известную метку/адрес."""
        self.rpn.append("$J")
        # Убедимся, что target_label является числом
        self.rpn.append(int(target_label))
        self.current_index += 2
        
    def replace_label_placeholder(self, old_value, new_value):
        """
        Заменяет заполнитель метки на реальное значение
        Ищет с конца списка для обработки вложенных конструкций
        """
        for i in range(len(self.rpn) - 1, -1, -1):
            if self.rpn[i] == old_value:
                self.rpn[i] = str(new_value)
                return True
        return False
        
    def get_current_index(self):
        """Возвращает текущий индекс в ОПС"""
        return self.current_index
        
    def get_rpn(self):
        """Возвращает сгенерированную ОПС"""
        return self.rpn
    
    def add_variable_access(self, var_name):
        self.rpn.append(var_name)

    def add_array_declaration(self, array_name):
        """
        Добавляет операцию объявления массива в ОПЗ.
        Размер массива будет на вершине стека ОПЗ во время выполнения.
        """
        self.rpn.append(array_name)
        self.rpn.append("DECL_ARR")

    def add_array_access(self, array_name):
        """
        Добавляет операцию доступа к элементам массива в ОПС.
        Ожидает, что индекс массива будет на вершине стека.
        """
        self.rpn.append(array_name)
        self.rpn.append("ACCESS_ARR")
