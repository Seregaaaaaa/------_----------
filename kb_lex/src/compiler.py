from .lexer import analyze
from .parser import Parser

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
        self.rpn = parser.parse()
        
        return self.rpn
    
    def get_tokens(self):
        """Возвращает список токенов после лексического анализа"""
        return self.tokens
    
    def get_rpn(self):
        """Возвращает обратную польскую запись (ОПС) после синтаксического анализа"""
        return self.rpn
