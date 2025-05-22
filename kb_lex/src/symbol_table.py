class SymbolTable:
    """
    Класс для управления таблицей символов программы
    Хранит информацию о переменных и их типах
    """
    
    def __init__(self):
        # Словари для различных типов переменных
        self.int_vars = {}  # Целочисленные переменные
        self.float_vars = {}  # Вещественные переменные
        self.int_arrays = {}  # Целочисленные массивы
        self.float_arrays = {}  # Вещественные массивы
        
    def add_variable(self, name, data_type):
        """
        Добавляет переменную в таблицу символов
        
        Args:
            name: Имя переменной
            data_type: Тип данных ('int', 'float', 'intarr', 'floatarr')
        
        Returns:
            bool: True если успешно добавлено, False если переменная уже существует
        """
        if self.exists(name):
            return False
        
        if data_type == 'int':
            self.int_vars[name] = 0  # Инициализация целой переменной
        elif data_type == 'float':
            self.float_vars[name] = 0.0  # Инициализация вещественной переменной
        elif data_type == 'intarr':
            self.int_arrays[name] = []  # Инициализация целочисленного массива
        elif data_type == 'floatarr':
            self.float_arrays[name] = []  # Инициализация вещественного массива
        else:
            raise ValueError(f"Неизвестный тип данных: {data_type}")
        
        return True
    
    def exists(self, name):
        """
        Проверяет, существует ли переменная в таблице символов
        
        Args:
            name: Имя переменной для проверки
            
        Returns:
            bool: True если переменная существует, иначе False
        """
        return (name in self.int_vars or 
                name in self.float_vars or 
                name in self.int_arrays or 
                name in self.float_arrays)
    
    def get_variable_type(self, name):
        """
        Возвращает тип переменной
        
        Args:
            name: Имя переменной
            
        Returns:
            str: Тип переменной ('int', 'float', 'intarr', 'floatarr') или None если не найдена
        """
        if name in self.int_vars:
            return 'int'
        elif name in self.float_vars:
            return 'float'
        elif name in self.int_arrays:
            return 'intarr'
        elif name in self.float_arrays:
            return 'floatarr'
        else:
            return None
    
    def is_array(self, name):
        """
        Проверяет, является ли переменная массивом
        
        Args:
            name: Имя переменной
            
        Returns:
            bool: True если переменная является массивом, иначе False
        """
        return name in self.int_arrays or name in self.float_arrays
