class SymbolTable:
    """
    Класс для управления таблицей символов программы.
    Хранит информацию о переменных: имя, тип, значение, является ли массивом,
    а также место объявления (строка, позиция).
    """
    
    def __init__(self):
        self.symbols = {}  # Словарь для хранения символов
        # Структура для каждого символа:
        # name -> {
        #     'base_type': str ('int', 'float'),
        #     'value': any (0, 0.0, list),
        #     'is_array': bool,
        #     'line': int,
        #     'position': int
        # }

    def add_symbol(self, name, base_type, line, position, is_array=False):
        """
        Добавляет символ (переменную или массив) в таблицу символов.

        Args:
            name (str): Имя символа.
            base_type (str): Базовый тип данных ('int', 'float').
            line (int): Номер строки объявления.
            position (int): Позиция в строке объявления.
            is_array (bool): True, если символ является массивом.

        Returns:
            bool: True если успешно добавлено.
        
        Raises:
            ValueError: Если символ уже существует или неизвестный базовый тип.
        """
        if name in self.symbols:
            # В реальном компиляторе здесь может быть ошибка переобъявления
            # Можно добавить self.symbols[name]['line'] и self.symbols[name]['position'] в сообщение
            raise ValueError(f"Ошибка: Символ '{name}' уже объявлен.")

        initial_value = None
        if is_array:
            initial_value = []  # Массивы инициализируются пустым списком, размер задается позже
        elif base_type == 'int':
            initial_value = 0
        elif base_type == 'float':
            initial_value = 0.0
        else:
            raise ValueError(f"Неизвестный базовый тип: {base_type} для символа '{name}'.")

        self.symbols[name] = {
            'base_type': base_type,
            'value': initial_value,
            'is_array': is_array,
            'line': line,
            'position': position
        }
        return True

    def exists(self, name):
        """
        Проверяет, существует ли символ в таблице.
        """
        return name in self.symbols

    def get_symbol_info(self, name):
        """
        Возвращает полную информацию о символе.
        """
        return self.symbols.get(name)

    def get_variable_type(self, name):
        """
        Возвращает базовый тип переменной.
        Для массивов возвращает тип элементов.
        """
        info = self.symbols.get(name)
        if info:
            return info['base_type']
        return None

    def is_array(self, name):
        """
        Проверяет, является ли символ массивом.
        """
        info = self.symbols.get(name)
        if info:
            return info['is_array']
        return False

    def get_value(self, name):
        """
        Получает значение переменной (не для массивов).
        """
        info = self.symbols.get(name)
        if info:
            if info['is_array']:
                raise ValueError(f"Ошибка: '{name}' является массивом. Используйте get_array_element.")
            return info['value']
        raise ValueError(f"Ошибка: Переменная '{name}' не найдена.")

    def set_value(self, name, value):
        """
        Устанавливает значение переменной (не для массивов).
        """
        info = self.symbols.get(name)
        if info:
            if info['is_array']:
                raise ValueError(f"Ошибка: '{name}' является массивом. Используйте set_array_element.")
            # Опционально: проверка типа значения перед присваиванием
            # if info['base_type'] == 'int' and not isinstance(value, int):
            #     raise TypeError(f"Тип значения для '{name}' должен быть int.")
            # if info['base_type'] == 'float' and not isinstance(value, (int, float)):
            #     raise TypeError(f"Тип значения для '{name}' должен быть float.")
            info['value'] = value
            return
        raise ValueError(f"Ошибка: Переменная '{name}' не найдена.")

    def get_array_element(self, name, index):
        """
        Получает значение элемента массива.
        """
        info = self.symbols.get(name)
        if info and info['is_array']:
            if not isinstance(index, int):
                raise TypeError(f"Индекс для массива '{name}' должен быть целым числом.")
            if 0 <= index < len(info['value']):
                return info['value'][index]
            else:
                raise IndexError(f"Индекс {index} вне границ для массива '{name}' (размер {len(info['value'])}).")
        raise ValueError(f"Ошибка: Массив '{name}' не найден или символ не является массивом.")

    def set_array_element(self, name, index, value):
        """
        Устанавливает значение элемента массива.
        """
        info = self.symbols.get(name)
        if info and info['is_array']:
            if not isinstance(index, int):
                raise TypeError(f"Индекс для массива '{name}' должен быть целым числом.")
            
            # Опционально: проверка типа значения
            # base_type = info['base_type']
            # if base_type == 'int' and not isinstance(value, int):
            #    raise TypeError(f"Тип значения для элементов '{name}' должен быть int.")
            # if base_type == 'float' and not isinstance(value, (int, float)):
            #    raise TypeError(f"Тип значения для элементов '{name}' должен быть float.")

            if 0 <= index < len(info['value']):
                info['value'][index] = value
            elif index == len(info['value']): # Разрешаем добавление в конец
                info['value'].append(value)
            else: # Если индекс больше текущего размера + 1, это ошибка или требует заполнения
                  # Пока что будем считать это ошибкой, если массив не был инициализирован до нужного размера
                raise IndexError(f"Индекс {index} вне границ для установки значения в массиве '{name}' (размер {len(info['value'])}). Используйте initialize_array для задания размера.")
            return
        raise ValueError(f"Ошибка: Массив '{name}' не найден или символ не является массивом.")

    def initialize_array(self, name, size):
        """
        Инициализирует массив заданным размером и значениями по умолчанию.
        Вызывается интерпретатором ОПЗ после вычисления размера массива.
        """
        info = self.symbols.get(name)
        if info and info['is_array']:
            if not isinstance(size, int) or size < 0:
                raise ValueError(f"Размер массива '{name}' должен быть неотрицательным целым числом.")
            
            base_type = info['base_type']
            default_val = 0 if base_type == 'int' else 0.0 if base_type == 'float' else None
            
            info['value'] = [default_val] * size
        else:
            raise ValueError(f"Ошибка: Невозможно инициализировать '{name}'. Символ не найден или не является массивом.")

    def __str__(self):
        return str(self.symbols)

# Пример использования (можно удалить или закомментировать)
if __name__ == '__main__':
    st = SymbolTable()
    st.add_symbol("var_int", "int", 1, 1)
    st.add_symbol("arr_float", "float", 2, 1, is_array=True)
    
    print(st.get_symbol_info("var_int"))
    st.set_value("var_int", 100)
    print(st.get_value("var_int"))

    st.initialize_array("arr_float", 5)
    print(st.get_symbol_info("arr_float"))
    st.set_array_element("arr_float", 0, 1.1)
    st.set_array_element("arr_float", 4, 5.5)
    print(st.get_array_element("arr_float", 0))
    print(st.get_symbol_info("arr_float"))

    try:
        st.add_symbol("var_int", "int", 5,5) # Повторное объявление
    except ValueError as e:
        print(e)

    try:
        st.set_value("arr_float", 10) # Попытка установить значение массиву как переменной
    except ValueError as e:
        print(e)
    
    try:
        st.get_array_element("var_int", 0) # Попытка доступа к переменной как к массиву
    except ValueError as e:
        print(e)

    try:
        st.set_array_element("arr_float", 10, 7.7) # Выход за границы (без предварительного initialize_array до этого индекса)
    except IndexError as e:
        print(e)
