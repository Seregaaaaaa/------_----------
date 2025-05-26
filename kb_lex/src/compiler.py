from .lexer import analyze
from .parser import Parser
from .rpn_interpreter import RPNInterpreter # Добавлен импорт интерпретатора

class Compiler:
    """
    Основной класс компилятора.
    Объединяет лексический анализатор и синтаксический анализатор,
    генерирует обратную польскую запись (ОПС).
    """
    
    def __init__(self):
        """Инициализация компилятора"""
        self.tokens = []  # Результат лексического анализа
        self.rpn = []     # Результат синтаксического анализа (ОПС)
        self.interpreter_output = [] # Результат выполнения программы
        self.symbol_table_after_execution = {} # Таблица символов после выполнения
        self.input_values = []  # Входные данные для программы
    
    def compile(self, source_code):
        """
        Выполняет компиляцию исходного кода:
        1. Лексический анализ
        2. Синтаксический анализ
        3. Генерация ОПС
        
        Args:
            source_code: Исходный код на языке компиляции
            
        Returns:
            list: Список команд ОПС
        """
        # Лексический анализ
        self.tokens = analyze(source_code)
        
        # Синтаксический анализ и генерация ОПС
        parser = Parser(self.tokens)
        rpn_result, symbol_table = parser.parse()
        self.rpn = rpn_result
        self.symbol_table_after_parsing = symbol_table
        
        return self.rpn
    
    def execute(self, source_code):
        """
        Компилирует и выполняет исходный код.

        Args:
            source_code: Исходный код на языке компиляции.

        Returns:
            tuple: (list_of_output, symbol_table_after_execution) 
                   или (None, None) в случае ошибки компиляции.
        Raises:
            Exception: Если во время выполнения ОПЗ возникает ошибка.
        """
        try:
            rpn_code = self.compile(source_code)
            if rpn_code is None: # Ошибка на этапе компиляции (уже обработана в parse)
                return None, None
        except Exception as e:
            # print(f"Ошибка компиляции: {e}") # Ошибка уже должна быть выведена парсером
            raise # Перевыбрасываем ошибку компиляции, чтобы ее увидел вызывающий код

        interpreter = RPNInterpreter()
        # Устанавливаем входные данные, если они есть
        if self.input_values:
            interpreter.set_input_values(self.input_values)
        
        try:
            self.interpreter_output, self.symbol_table_after_execution = interpreter.interpret(rpn_code)
            return self.interpreter_output, self.symbol_table_after_execution
        except Exception as e:
            # print(f"Ошибка выполнения ОПЗ: {e}")
            raise # Перевыбрасываем ошибку выполнения, чтобы ее увидел вызывающий код

    def get_tokens(self):
        """Возвращает список токенов после лексического анализа"""
        return self.tokens
    
    def get_rpn(self):
        """Возвращает обратную польскую запись (ОПС) после синтаксического анализа"""
        return self.rpn
    
    def get_interpreter_output(self):
        """Возвращает вывод программы после выполнения ОПЗ"""
        return self.interpreter_output
    
    def get_symbol_table_after_execution(self):
        """Возвращает таблицу символов после выполнения ОПЗ"""
        return self.symbol_table_after_execution
    
    def set_input_values(self, input_values):
        """Устанавливает входные данные для программы"""
        self.input_values = input_values
