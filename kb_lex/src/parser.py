from .token_type import TokenType
from .token_1 import Token
from .rpn_generator import RPNGenerator
from .symbol_table import SymbolTable

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # Список токенов от лексического анализатора
        self.current_index = 0  # Индекс текущего токена
        self.stack = []  # Магазин (стек) для синтаксического анализатора
        self.rpn_generator = RPNGenerator()  # Генератор ОПС
        self.symbol_table = SymbolTable()  # Таблица символов
        self.data_types_stack = []  # Стек для хранения типов данных
        self.label_stack = []  # Стек для хранения меток (адресов) для операторов перехода
        
        # Контекстная информация
        self.context = {
            "in_array_declaration": False,  # Находимся в объявлении массива
            "in_array_initialization": False,  # Находимся в инициализации массива
            "in_variable_declaration": False,  # Находимся в объявлении переменной
            "in_assignment": False,  # Находимся в операторе присваивания
            "in_if_condition": False,  # Находимся в условии if
            "in_while_condition": False,  # Находимся в условии while
            "in_expression": False,  # Находимся в выражении
            "in_logical_expression": False,  # Находимся в логическом выражении
            "current_operator": None,  # Текущий обрабатываемый оператор
            "last_identifier": None,  # Последний обработанный идентификатор
            "last_token": None  # Последний обработанный токен
        }
        
        # Инициализация стека и начало разбора
        self.stack.append(TokenType.EOF)
        self.stack.append("<Программа>")
        
    def current_token(self):
        """Возвращает текущий токен или токен EOF, если достигнут конец списка"""
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        # Возвращаем токен конца файла, если индекс за пределами списка
        return Token(TokenType.EOF, "", -1, -1)
    
    def advance(self):
        """Переход к следующему токену"""
        self.current_index += 1
        
    def match(self, token_type):
        """Проверяет, соответствует ли текущий токен ожидаемому типу"""
        if self.current_token().token_type == token_type:
            self.advance()
            return True
        return False
    
    def error(self, message):
        """Обработка синтаксической ошибки"""
        token = self.current_token()
        raise SyntaxError(f"Синтаксическая ошибка в строке {token.line}, позиция {token.position}: {message}")
    
    def build_parse_table(self):
        """
        Строит таблицу синтаксического анализа для LL(1) парсера на основе грамматики в форме Грейбаха
        Возвращает словарь: {нетерминал: {терминал: список правил}}
        """
        table = {}
        
        # Правила для <Программа>
        table["<Программа>"] = {
            TokenType.INT: [TokenType.INT, "<ОператорDT>", "<Список операторов>"],
            TokenType.FLOAT: [TokenType.FLOAT, "<ОператорDT>", "<Список операторов>"],
            TokenType.IF: [TokenType.IF, TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Блок>", "<Альтернативное действие>", "<Список операторов>"],
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ПрисваиваниеIdent>", TokenType.SEMICOLON, "<Список операторов>"],
            TokenType.WHILE: [TokenType.WHILE, TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Блок>", "<Список операторов>"],
            TokenType.INPUT: [TokenType.INPUT, "<ВводInput>", "<Список операторов>"],
            TokenType.OUTPUT: [TokenType.OUTPUT, "<Логическое выражение>", TokenType.SEMICOLON, "<Список операторов>"]
        }
        
        # Правила для <ОператорDT>
        table["<ОператорDT>"] = {
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ОператорDTIdent>", TokenType.SEMICOLON],
            TokenType.LSQUARE: [TokenType.LSQUARE, TokenType.RSQUARE, TokenType.IDENTIFIER, "<ОператорDTIdent>", TokenType.SEMICOLON]
        }
        
        # Правила для <Список операторов>
        table["<Список операторов>"] = {
            TokenType.INT: [TokenType.INT, "<ОператорDT>", "<Список операторов>"],
            TokenType.FLOAT: [TokenType.FLOAT, "<ОператорDT>", "<Список операторов>"],
            TokenType.IF: [TokenType.IF, TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Блок>", "<Альтернативное действие>", "<Список операторов>"],
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ПрисваиваниеIdent>", TokenType.SEMICOLON, "<Список операторов>"],
            TokenType.WHILE: [TokenType.WHILE, TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Блок>", "<Список операторов>"],
            TokenType.INPUT: [TokenType.INPUT, "<ВводInput>", "<Список операторов>"],
            TokenType.OUTPUT: [TokenType.OUTPUT, "<Логическое выражение>", TokenType.SEMICOLON, "<Список операторов>"],
        }
        
        # Пустой список (lambda) для всех остальных токенов в <Список операторов>
        for token_type in TokenType:
            if token_type not in [TokenType.INT, TokenType.FLOAT, TokenType.IF, 
                                  TokenType.IDENTIFIER, TokenType.WHILE, 
                                  TokenType.INPUT, TokenType.OUTPUT]:
                if "<Список операторов>" not in table:
                    table["<Список операторов>"] = {}
                table["<Список операторов>"][token_type] = []  # lambda (пустое правило)
        
        # Правила для <Инициализаторы>
        table["<Инициализаторы>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>", "<Инициализаторы*>"],
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ФакторIdent>", "<Терм*>", "<Выражение*>", "<Инициализаторы*>"],
            TokenType.INTEGER_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Инициализаторы*>"],
            TokenType.FLOAT_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Инициализаторы*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>", "<Выражение*>", "<Инициализаторы*>"]
        }
        
        # Правила для <Инициализаторы*>
        table["<Инициализаторы*>"] = {
            TokenType.COMMA: [TokenType.COMMA, "<Выражение>", "<Инициализаторы*>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.COMMA:
                if "<Инициализаторы*>" not in table:
                    table["<Инициализаторы*>"] = {}
                table["<Инициализаторы*>"][token_type] = []  # lambda
        
        # Правила для <Альтернативное действие>
        table["<Альтернативное действие>"] = {
            TokenType.ELSE: [TokenType.ELSE, "<Блок>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.ELSE:
                if "<Альтернативное действие>" not in table:
                    table["<Альтернативное действие>"] = {}
                table["<Альтернативное действие>"][token_type] = []  # lambda
        
        # Правила для <Блок>
        table["<Блок>"] = {
            TokenType.LCURLY: [TokenType.LCURLY, "<Список операторов>", TokenType.RCURLY]
        }
        
        # Правила для <Логическое выражение>
        table["<Логическое выражение>"] = {
            TokenType.UNARY_MINUS: ["~", "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>", "<Логическое выражение*>"],
            TokenType.IDENTIFIER: ["идентификатор", "<ФакторIdent>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>", "<Логическое выражение*>"],
            TokenType.INTEGER_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>", "<Логическое выражение*>"],
            TokenType.FLOAT_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>", "<Логическое выражение*>"],
            TokenType.LPAREN: ["(", "<Логическое выражение>", ")", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>", "<Логическое выражение*>"]
        }
        
        # Правила для <Логическое выражение*>
        table["<Логическое выражение*>"] = {
            TokenType.OR: ["|", "<Логическое И>", "<Логическое выражение*>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.OR:
                if "<Логическое выражение*>" not in table:
                    table["<Логическое выражение*>"] = {}
                table["<Логическое выражение*>"][token_type] = []  # lambda
        
        # Правила для <Логическое И>
        table["<Логическое И>"] = {
            TokenType.UNARY_MINUS: ["~", "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>"],
            TokenType.IDENTIFIER: ["идентификатор", "<ФакторIdent>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>"],
            TokenType.INTEGER_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>"],
            TokenType.FLOAT_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>"],
            TokenType.LPAREN: ["(", "<Логическое выражение>", ")", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<Логическое И*>"]
        }
        
        # Правила для <Логическое И*>
        table["<Логическое И*>"] = {
            TokenType.AND: ["&", "<Проверка равенства>", "<Логическое И*>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.AND:
                if "<Логическое И*>" not in table:
                    table["<Логическое И*>"] = {}
                table["<Логическое И*>"][token_type] = []  # lambda
        
        # Правила для <ОператорDTIdent>
        table["<ОператорDTIdent>"] = {
            TokenType.ASSIGN: [TokenType.ASSIGN, "<Выражение>"],
            TokenType.LSQUARE: [TokenType.LSQUARE, TokenType.INTEGER_CONST, TokenType.RSQUARE, TokenType.ASSIGN, "<Выражение>"],
        }
        for token_type in TokenType:
            if token_type not in [TokenType.ASSIGN, TokenType.LSQUARE]:
                if "<ОператорDTIdent>" not in table:
                    table["<ОператорDTIdent>"] = {}
                table["<ОператорDTIdent>"][token_type] = []  # lambda
        
        # Правила для <ПрисваиваниеIdent>
        table["<ПрисваиваниеIdent>"] = {
            TokenType.ASSIGN: [TokenType.ASSIGN, "<Выражение>"],
            TokenType.LSQUARE: [TokenType.LSQUARE, "<Логическое выражение>", TokenType.RSQUARE, TokenType.ASSIGN, "<Выражение>"]
        }
        
        # Правила для <Выражение>
        table["<Выражение>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>"],
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ФакторIdent>", "<Терм*>", "<Выражение*>"],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>", "<Выражение*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>", "<Выражение*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>", "<Выражение*>"],
            TokenType.LCURLY: [TokenType.LCURLY, "<Инициализаторы>", TokenType.RCURLY]
        }
        
        # Правила для <Выражение*>
        table["<Выражение*>"] = {
            TokenType.PLUS: [TokenType.PLUS, "<Терм>", "<Выражение*>"],
            TokenType.MINUS: [TokenType.MINUS, "<Терм>", "<Выражение*>"]
        }
        for token_type in TokenType:
            if token_type not in [TokenType.PLUS, TokenType.MINUS]:
                if "<Выражение*>" not in table:
                    table["<Выражение*>"] = {}
                table["<Выражение*>"][token_type] = []  # lambda
        
        # Правила для <Терм>
        table["<Терм>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>"],
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ФакторIdent>", "<Терм*>"],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>"]
        }
        
        # Правила для <Терм*>
        table["<Терм*>"] = {
            TokenType.MULTIPLY: [TokenType.MULTIPLY, "<Фактор>", "<Терм*>"],
            TokenType.DIVIDE: [TokenType.DIVIDE, "<Фактор>", "<Терм*>"]
        }
        for token_type in TokenType:
            if token_type not in [TokenType.MULTIPLY, TokenType.DIVIDE]:
                if "<Терм*>" not in table:
                    table["<Терм*>"] = {}
                table["<Терм*>"][token_type] = []  # lambda
        
        # Правила для <Фактор>
        table["<Фактор>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>"],
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ФакторIdent>"],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN]
        }
        
        # Правила для <ФакторIdent>
        table["<ФакторIdent>"] = {
            TokenType.LSQUARE: [TokenType.LSQUARE, "<Логическое выражение>", TokenType.RSQUARE]
        }
        for token_type in TokenType:
            if token_type != TokenType.LSQUARE:
                if "<ФакторIdent>" not in table:
                    table["<ФакторIdent>"] = {}
                table["<ФакторIdent>"][token_type] = []  # lambda
        
        # Правила для <ВводInput>
        table["<ВводInput>"] = {
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ВводInputIdent>", TokenType.SEMICOLON]
        }
        
        # Правила для <ВводInputIdent>
        table["<ВводInputIdent>"] = {
            TokenType.LSQUARE: [TokenType.LSQUARE, "<Логическое выражение>", TokenType.RSQUARE]
        }
        for token_type in TokenType:
            if token_type != TokenType.LSQUARE:
                if "<ВводInputIdent>" not in table:
                    table["<ВводInputIdent>"] = {}
                table["<ВводInputIdent>"][token_type] = []  # lambda
        
        # Правила для <Сравнение>
        table["<Сравнение>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*>"],
            TokenType.IDENTIFIER: [TokenType.IDENTIFIER, "<ФакторIdent>", "<Терм*>", "<Выражение*>", "<Сравнение*>"],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>", "<Выражение*>", "<Сравнение*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>", "<Выражение*>", "<Сравнение*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>", "<Выражение*>", "<Сравнение*>"]
        }
        
        # Правила для <Сравнение*>
        table["<Сравнение*>"] = {
            TokenType.LT: [TokenType.LT, "<Выражение>", "<Сравнение*>"],
            TokenType.GT: [TokenType.GT, "<Выражение>", "<Сравнение*>"]
        }
        for token_type in TokenType:
            if token_type not in [TokenType.LT, TokenType.GT]:
                if "<Сравнение*>" not in table:
                    table["<Сравнение*>"] = {}
                table["<Сравнение*>"][token_type] = []  # lambda
        
        # Правила для <Проверка равенства>
        table["<Проверка равенства>"] = {
            TokenType.UNARY_MINUS: ["~", "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>"],
            TokenType.IDENTIFIER: ["идентификатор", "<ФакторIdent>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>"],
            TokenType.INTEGER_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>"],
            TokenType.FLOAT_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>"],
            TokenType.LPAREN: ["(", "<Логическое выражение>", ")", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>"]
        }
        
        # Правила для <Проверка равенства*>
        table["<Проверка равенства*>"] = {
            TokenType.EQ: ["?", "<Сравнение>", "<Проверка равенства*>"],
            TokenType.NEQ: ["!", "<Сравнение>", "<Проверка равенства*>"]
        }
        for token_type in TokenType:
            if token_type not in [TokenType.EQ, TokenType.NEQ]:
                if "<Проверка равенства*>" not in table:
                    table["<Проверка равенства*>"] = {}
                table["<Проверка равенства*>"][token_type] = []
        
        # Аналогично добавляем остальные правила
        
        return table
        
    def parse(self):
        """
        Выполняет синтаксический анализ и генерацию ОПС
        Возвращает список команд ОПС
        """
        parse_table = self.build_parse_table()
        semantic_actions = self.build_semantic_actions()
        
        while self.stack:
            top = self.stack[-1]  # Смотрим на верхний символ стека (без удаления)
            current_token = self.current_token()
            
            # Отладочная информация
            print(f"Стек: {top}, Токен: {current_token.token_type} = {current_token.value}")
            
            # Проверяем наличие семантических действий для данного состояния
            if top in semantic_actions:
                action = semantic_actions[top]
                self.execute_semantic_action(action)
            
            # Удаляем верхний символ стека
            self.stack.pop()
            
            if self.is_terminal(top):
                # Если верхний символ стека - терминал
                if top == TokenType.EOF and current_token.token_type == TokenType.EOF:
                    # Достигнут конец файла
                    break
                
                elif top == TokenType.EOF:
                    self.error(f"Неожиданный конец разбора, ожидался EOF, получен {current_token.token_type}")
                
                elif (isinstance(top, TokenType) and top == current_token.token_type) or \
                     (top == "идентификатор" and current_token.token_type == TokenType.IDENTIFIER) or \
                     (top == "константа" and (current_token.token_type == TokenType.INTEGER_CONST or current_token.token_type == TokenType.FLOAT_CONST)) or \
                     (isinstance(top, str) and top in ["(", ")", "{", "}", "[", "]", ",", ";", "+", "-", "*", "/", "<", ">", "=", "!", "?", "&", "|", "~"]):
                    
                    # Обработка совпадения токена с терминалом
                    if top == "идентификатор" or (isinstance(top, TokenType) and top == TokenType.IDENTIFIER):
                        # Добавление идентификатора в ОПС
                        self.rpn_generator.add_identifier(current_token.value)
                    elif top == "константа" or (isinstance(top, TokenType) and (top == TokenType.INTEGER_CONST or top == TokenType.FLOAT_CONST)):
                        # Добавление константы в ОПС
                        self.rpn_generator.add_constant(current_token.value)
                    elif top == "int" or (isinstance(top, TokenType) and top == TokenType.INT):
                        # Программа 1: Записать тип в стек типов
                        self.data_types_stack.append("int")
                    elif top == "float" or (isinstance(top, TokenType) and top == TokenType.FLOAT):
                        # Программа 1: Записать тип в стек типов
                        self.data_types_stack.append("float")
                    # Обработка операторов в строковом представлении
                    elif top == "?" and current_token.token_type == TokenType.EQ:
                        pass
                    elif top == "!" and current_token.token_type == TokenType.NEQ:
                        pass
                    elif top == "&" and current_token.token_type == TokenType.AND:
                        pass
                    elif top == "|" and current_token.token_type == TokenType.OR:
                        pass
                    elif top == "~" and current_token.token_type == TokenType.UNARY_MINUS:
                        pass
                    elif top == "+" and current_token.token_type == TokenType.PLUS:
                        pass
                    elif top == "-" and current_token.token_type == TokenType.MINUS:
                        pass
                    elif top == "*" and current_token.token_type == TokenType.MULTIPLY:
                        pass
                    elif top == "/" and current_token.token_type == TokenType.DIVIDE:
                        pass
                    elif top == "<" and current_token.token_type == TokenType.LT:
                        pass
                    elif top == ">" and current_token.token_type == TokenType.GT:
                        pass
                    elif top == "=" and current_token.token_type == TokenType.ASSIGN:
                        pass
                    elif top == "(" and current_token.token_type == TokenType.LPAREN:
                        pass
                    elif top == ")" and current_token.token_type == TokenType.RPAREN:
                        pass
                    elif top == "[" and current_token.token_type == TokenType.LSQUARE:
                        pass
                    elif top == "]" and current_token.token_type == TokenType.RSQUARE:
                        pass
                    elif top == "{" and current_token.token_type == TokenType.LCURLY:
                        pass
                    elif top == "}" and current_token.token_type == TokenType.RCURLY:
                        pass
                    elif top == ";" and current_token.token_type == TokenType.SEMICOLON:
                        pass
                    elif top == "," and current_token.token_type == TokenType.COMMA:
                        pass
                    
                    self.advance()  # Переходим к следующему токену
                else:
                    self.error(f"Ожидался {top}, но получен {current_token.token_type}")
            
            elif self.is_nonterminal(top):
                # Если верхний символ стека - нетерминал
                
                # Проверка наличия правила в таблице разбора
                if top in parse_table and current_token.token_type in parse_table[top]:
                    # Получаем правило из таблицы разбора
                    rule = parse_table[top][current_token.token_type]
                    
                    # Добавляем символы в стек в обратном порядке (только если правило не пустое)
                    if rule:  # Проверяем, что правило не пустое (не лямбда)
                        for symbol in reversed(rule):
                            self.stack.append(symbol)
                else:
                    # Проверяем, есть ли правило для всех терминалов (лямбда)
                    if top in parse_table:
                        handled = False
                        for token_type in parse_table[top]:
                            if parse_table[top][token_type] == [] and not handled:
                                # Пустое правило (лямбда)
                                handled = True
                                break
                        
                        if not handled:
                            self.error(f"Нет правила для {top} с токеном {current_token.token_type}")
                    else:
                        self.error(f"Нетерминал {top} не найден в таблице разбора")
            
            else:
                # Обработка операторов и специальных символов
                if top == "+":
                    self.rpn_generator.add_operator("+")
                elif top == "-":
                    self.rpn_generator.add_operator("-")
                elif top == "*":
                    self.rpn_generator.add_operator("*")
                elif top == "/":
                    self.rpn_generator.add_operator("/")
                elif top == "<":
                    self.rpn_generator.add_operator("<")
                elif top == ">":
                    self.rpn_generator.add_operator(">")
                elif top == "!":
                    self.rpn_generator.add_operator("!")
                elif top == "?":
                    self.rpn_generator.add_operator("?")
                elif top == "&":
                    self.rpn_generator.add_operator("&")
                elif top == "|":
                    self.rpn_generator.add_operator("|")
                elif top == "~":
                    self.rpn_generator.add_operator("~")
                elif top == "=":
                    self.rpn_generator.add_operator("=")
                elif isinstance(top, TokenType):
                    # Обработка TokenType операторов
                    if top == TokenType.PLUS:
                        self.rpn_generator.add_operator("+")
                    elif top == TokenType.MINUS:
                        self.rpn_generator.add_operator("-")
                    elif top == TokenType.MULTIPLY:
                        self.rpn_generator.add_operator("*")
                    elif top == TokenType.DIVIDE:
                        self.rpn_generator.add_operator("/")
                    elif top == TokenType.LT:
                        self.rpn_generator.add_operator("<")
                    elif top == TokenType.GT:
                        self.rpn_generator.add_operator(">")
                    elif top == TokenType.NEQ:
                        self.rpn_generator.add_operator("!")
                    elif top == TokenType.EQ:
                        self.rpn_generator.add_operator("?")
                    elif top == TokenType.AND:
                        self.rpn_generator.add_operator("&")
                    elif top == TokenType.OR:
                        self.rpn_generator.add_operator("|")
                    elif top == TokenType.UNARY_MINUS:
                        self.rpn_generator.add_operator("~")
                    elif top == TokenType.ASSIGN:
                        self.rpn_generator.add_operator("=")
                elif top == TokenType.LSQUARE or top == "[":
                    # Программа 2: Дописать признак массива к типу
                    if self.data_types_stack and self.context["in_array_declaration"]:
                        current_type = self.data_types_stack.pop()
                        self.data_types_stack.append(current_type + "arr")
                elif top == "EOF" or top == TokenType.EOF:
                    # Конец разбора
                    if current_token.token_type != TokenType.EOF:
                        self.error(f"Ожидался конец файла, но получен {current_token.token_type}")
                    break
        
        return self.rpn_generator.get_rpn()
    
    def is_terminal(self, symbol):
        """Проверяет, является ли символ терминальным"""
        terminal_strings = ["идентификатор", "константа", "(", ")", "{", "}", "[", "]", 
                         ",", ";", "+", "-", "*", "/", "<", ">", "=", "!", "?", 
                         "&", "|", "~", "int", "float", "if", "else", "while", 
                         "input", "output", "EOF"]
        
        return isinstance(symbol, TokenType) or symbol in terminal_strings
    
    def is_nonterminal(self, symbol):
        """Проверяет, является ли символ нетерминальным"""
        return isinstance(symbol, str) and symbol.startswith("<") and symbol.endswith(">")
    
    def build_semantic_actions(self):
        """
        Строит словарь семантических действий для различных контекстов
        Возвращает словарь: {символ или состояние: действие}
        """
        actions = {}
        
        # Семантические программы для нетерминалов
        actions["<while>"] = "program6"  # Начало цикла while
        actions["<after_while_condition>"] = "program7"  # После условия while
        actions["<end_while_block>"] = "program8"  # Конец блока while
        actions["<after_if_condition>"] = "program9"  # После условия if
        actions["<end_if_block>"] = "program10"  # Конец блока if без else
        actions["<start_else_block>"] = "program11"  # Начало блока else
        
        # Семантические программы для операторов и других контекстов
        actions["output"] = "add_w"  # Добавить операцию вывода
        actions["input"] = "add_r"  # Добавить операцию ввода
        actions["["] = "array_index"  # Индексация массива
        actions["$init"] = "init_array"  # Инициализация массива
        
        return actions
    
    def execute_semantic_action(self, action):
        """Выполняет семантическую программу"""
        if action == "program6":
            # Программа 6: Начало цикла while
            self.label_stack.append(str(self.rpn_generator.get_current_index()))
            
        elif action == "program7":
            # Программа 7: После условия while
            self.label_stack.append(str(self.rpn_generator.get_current_index()))
            self.rpn_generator.add_conditional_jump()  # jf с заполнителем
            
        elif action == "program8":
            # Программа 8: Конец блока while
            jf_addr = self.label_stack.pop()  # Адрес команды jf
            start_addr = self.label_stack.pop()  # Адрес начала цикла
            
            # Заполняем метку для jf
            self.rpn_generator.replace_label_placeholder("_", str(self.rpn_generator.get_current_index() + 2))
            
            # Добавляем безусловный переход на начало цикла
            self.rpn_generator.add_jump(start_addr)
            
        elif action == "program9":
            # Программа 9: После условия if
            self.label_stack.append(str(self.rpn_generator.get_current_index()))
            self.rpn_generator.add_conditional_jump()  # jf с заполнителем
            
        elif action == "program10":
            # Программа 10: Конец if без else
            jf_addr = self.label_stack.pop()  # Адрес команды jf
            # Заполняем метку для jf
            self.rpn_generator.replace_label_placeholder("_", str(self.rpn_generator.get_current_index()))
            
        elif action == "program11":
            # Программа 11: Начало блока else
            jf_addr = self.label_stack.pop()  # Адрес команды jf (из программы 9)
            
            # Записываем адрес текущей команды j
            self.label_stack.append(str(self.rpn_generator.get_current_index()))
            
            # Добавляем безусловный переход для пропуска блока else
            self.rpn_generator.add_jump(None)  # j с заполнителем
            
            # Заполняем метку для jf из программы 9 (переход на начало блока else)
            self.rpn_generator.replace_label_placeholder("_", str(self.rpn_generator.get_current_index()))
            
        elif action == "add_w":
            # Добавить операцию вывода
            self.rpn_generator.add_operator("w")
            
        elif action == "add_r":
            # Добавить операцию ввода
            self.rpn_generator.add_operator("r")
            
        elif action == "array_index":
            # Индексация массива
            self.rpn_generator.add_operator("i")
        
        elif action == "init_array":
            # Инициализация массива
            self.rpn_generator.add_operator("init")
    
    def handle_variable_declaration(self, identifier):
        """Обрабатывает объявление переменной"""
        if not self.data_types_stack:
            self.error(f"Ошибка: тип данных не определен для {identifier}")
            return
        
        data_type = self.data_types_stack.pop()
        
        # Проверка на повторное объявление
        if self.symbol_table.exists(identifier):
            self.error(f"Ошибка: повторное объявление '{identifier}'")
            return
        
        # Добавляем переменную в таблицу символов
        self.symbol_table.add_variable(identifier, data_type)
        
        # Добавляем идентификатор в ОПС
        self.rpn_generator.add_identifier(identifier)
    
    def handle_array_declaration(self, identifier):
        """Обрабатывает объявление массива"""
        if not self.data_types_stack:
            self.error(f"Ошибка: тип данных не определен для массива {identifier}")
            return
        
        data_type = self.data_types_stack.pop()
        
        # Проверка, что тип содержит признак массива
        if not data_type.endswith("arr"):
            self.error(f"Ошибка: ожидался тип массива, получен {data_type}")
            return
        
        # Проверка на повторное объявление
        if self.symbol_table.exists(identifier):
            self.error(f"Ошибка: повторное объявление '{identifier}'")
            return
        
        # Добавляем массив в таблицу символов
        self.symbol_table.add_variable(identifier, data_type)
        
        # Добавляем идентификатор в ОПС
        self.rpn_generator.add_identifier(identifier)
        
        # Для инициализации массива с помощью списка {...}
        if self.context["in_array_initialization"]:
            self.rpn_generator.add_operator("GEN")
    
    def is_terminal(self, symbol):
        """Проверяет, является ли символ терминальным"""
        terminal_strings = ["идентификатор", "константа", "(", ")", "{", "}", "[", "]", 
                          ",", ";", "+", "-", "*", "/", "<", ">", "=", "!", "?", 
                          "&", "|", "~", "int", "float", "if", "else", "while", 
                          "input", "output", "EOF"]
        
        # Проверка на TokenType или строковые представления терминалов
        return isinstance(symbol, TokenType) or symbol in terminal_strings
    
    def is_nonterminal(self, symbol):
        """Проверяет, является ли символ нетерминальным"""
        return isinstance(symbol, str) and symbol.startswith("<") and symbol.endswith(">")


class SyntaxError(Exception):
    """Исключение для синтаксических ошибок"""
    pass
