class RPNGenerator:
    """
    Класс для генерации обратной польской записи (ОПС)
    на основе результатов синтаксического анализа
    """
    
    def __init__(self):
        self.rpn = []  # Список команд ОПС
        self.current_index = 0  # Текущий индекс в ОПС
        
    def add_identifier(self, name):
        """
        Добавляет идентификатор переменной в ОПС
        a <идентификатор> -> <идентификатор переменной>
        """
        self.rpn.append(name)
        self.current_index += 1
        
    def add_constant(self, value):
        """
        Добавляет константу в ОПС
        k <константа> -> <число>
        """
        self.rpn.append(str(value))
        self.current_index += 1
        
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
            'w': "$w",  # output (вывод)
            'r': "$r",  # input (ввод)
            'i': "$i",  # индексация массива
            'init': "LIST",  # начало инициализации массива
            'GEN': "$GEN",  # завершение инициализации массива
        }
        
        if operator in operator_map:
            self.rpn.append(operator_map[operator])
            self.current_index += 1
        else:
            raise ValueError(f"Неизвестный оператор: {operator}")
        
    def add_jump(self, label):
        """
        Добавляет безусловный переход в ОПС
        j <метка> -> $J <метка>
        """
        self.rpn.append("$J")
        self.rpn.append(str(label))
        self.current_index += 2
        
    def add_conditional_jump(self, label=None):
        """
        Добавляет условный переход в ОПС
        jf <метка> -> $JF <метка>
        Если метка не указана, добавляется заполнитель "_"
        """
        self.rpn.append("$JF")
        if label is None:
            self.rpn.append("_")  # Заполнитель для последующей подстановки метки
        else:
            self.rpn.append(str(label))
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
