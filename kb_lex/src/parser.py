from .token_type import TokenType
from .token_1 import Token
from .rpn_generator import RPNGenerator
from .symbol_table import SymbolTable

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  
        self.current_index = 0  
        self.stack = []  
        self.rpn_generator = RPNGenerator()  
        self.symbol_table = SymbolTable()  
        self.data_types_stack = []  
        self.label_stack = []  
        

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
        

        self.stack.append(TokenType.EOF)
        self.stack.append("<Программа>")
        
    def current_token(self):
        """Возвращает текущий токен или токен EOF, если достигнут конец списка"""
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]

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
        Строит таблицу синтаксического анализа для LL(1) парсера на основе грамматики в форме Грейбаха.
        Возвращает словарь: {нетерминал: {терминал: список правил}}
        """
        table = {}
        
        # <Программа>
        table["<Программа>"] = {
            TokenType.INT: ["<push_int_type>", TokenType.INT, "<ОператорDT>", "<Список операторов>"],
            TokenType.FLOAT: ["<push_float_type>", TokenType.FLOAT, "<ОператорDT>", "<Список операторов>"],
            TokenType.IF: [TokenType.IF, TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<after_if_condition>", "<Блок>", "<Альтернативное действие_extended>", "<Список операторов>"],
            TokenType.IDENTIFIER: ["<save_identifier_token>", TokenType.IDENTIFIER, "<ПрисваиваниеIdent>", TokenType.SEMICOLON, "<Список операторов>"],
            TokenType.WHILE: [TokenType.WHILE, "<while>", TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<after_while_condition>", "<Блок>", "<end_while_block>", "<Список операторов>"],
            TokenType.INPUT: [TokenType.INPUT, "<ВводInput>", "<Список операторов>"],
            TokenType.OUTPUT: [TokenType.OUTPUT, "<Логическое выражение>", "<gen_output_op>", TokenType.SEMICOLON, "<Список операторов>"]
        }
        
        # <ОператорDT>
        table["<ОператорDT>"] = {
            TokenType.IDENTIFIER: [
                "<save_identifier_token>", 
                TokenType.IDENTIFIER, 
                "<add_variable_declaration>", 
                "<ОператорDTIdent>", 
                TokenType.SEMICOLON
            ],
            TokenType.LSQUARE: [
                TokenType.LSQUARE, 
                "<ОператорDT_array>"
            ]
        }
        
        # <ОператорDT_array> - для обработки объявлений массивов
        table["<ОператорDT_array>"] = {
            # int [expr] identifier; - массив с заданным размером
            TokenType.UNARY_MINUS: [
                "<Выражение>", 
                TokenType.RSQUARE, 
                "<save_identifier_token>", 
                TokenType.IDENTIFIER, 
                "<add_dynamic_array_declaration>", 
                TokenType.SEMICOLON
            ],
            TokenType.IDENTIFIER: [
                "<Выражение>", 
                TokenType.RSQUARE, 
                "<save_identifier_token>", 
                TokenType.IDENTIFIER, 
                "<add_dynamic_array_declaration>", 
                TokenType.SEMICOLON
            ],
            TokenType.INTEGER_CONST: [
                "<Выражение>", 
                TokenType.RSQUARE, 
                "<save_identifier_token>", 
                TokenType.IDENTIFIER, 
                "<add_dynamic_array_declaration>", 
                TokenType.SEMICOLON
            ],
            TokenType.FLOAT_CONST: [
                "<Выражение>", 
                TokenType.RSQUARE, 
                "<save_identifier_token>", 
                TokenType.IDENTIFIER, 
                "<add_dynamic_array_declaration>", 
                TokenType.SEMICOLON
            ],
            TokenType.LPAREN: [
                "<Выражение>", 
                TokenType.RSQUARE, 
                "<save_identifier_token>", 
                TokenType.IDENTIFIER, 
                "<add_dynamic_array_declaration>", 
                TokenType.SEMICOLON
            ],
            # int [] identifier = { ... }; - инициализация массива списком
            TokenType.RSQUARE: [
                TokenType.RSQUARE, 
                "<save_identifier_token>", 
                TokenType.IDENTIFIER, 
                "<add_array_declaration_for_init>", 
                TokenType.ASSIGN, 
                "<gen_array_init_start>",
                TokenType.LCURLY, 
                "<Инициализаторы>", 
                TokenType.RCURLY,
                "<gen_array_init_end>",
                TokenType.SEMICOLON
            ]
        }
        
        # <Список операторов>
        table["<Список операторов>"] = {
            TokenType.INT: ["<push_int_type>", TokenType.INT, "<ОператорDT>", "<Список операторов>"],
            TokenType.FLOAT: ["<push_float_type>", TokenType.FLOAT, "<ОператорDT>", "<Список операторов>"],
            TokenType.IF: [TokenType.IF, TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<after_if_condition>", "<Блок>", "<Альтернативное действие_extended>", "<Список операторов>"],
            TokenType.IDENTIFIER: ["<save_identifier_token>", TokenType.IDENTIFIER, "<ПрисваиваниеIdent>", TokenType.SEMICOLON, "<Список операторов>"],
            TokenType.WHILE: [TokenType.WHILE, "<while>", TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<after_while_condition>", "<Блок>", "<end_while_block>", "<Список операторов>"],
            TokenType.INPUT: [TokenType.INPUT, "<ВводInput>", "<Список операторов>"],
            TokenType.OUTPUT: [TokenType.OUTPUT, "<Логическое выражение>", "<gen_output_op>", TokenType.SEMICOLON, "<Список операторов>"],
        }
        explicitly_defined_tokens_for_list_ops = list(table["<Список операторов>"].keys())
        for token_type in TokenType:
            if token_type not in explicitly_defined_tokens_for_list_ops:
                table["<Список операторов>"][token_type] = []

        # <Инициализаторы>
        table["<Инициализаторы>"] = {}
        # Токены, которые могут начинать выражение (первый элемент списка или вложенный инициализатор).
        # Они соответствуют начальным токенам для нетерминала <Выражение>.
        expression_starter_tokens = [
            TokenType.UNARY_MINUS, TokenType.IDENTIFIER, TokenType.INTEGER_CONST,
            TokenType.FLOAT_CONST, TokenType.LPAREN, TokenType.LCURLY
        ]
        for token_type in expression_starter_tokens:
            table["<Инициализаторы>"][token_type] = ["<Выражение>", "<Инициализаторы_продолжение>"]
        
        # Правило для пустого списка инициализаторов: например, int arr[] = {};
        # Когда <Инициализаторы> на вершине стека, а следующий токен RCURLY.
        table["<Инициализаторы>"][TokenType.RCURLY] = [] # Эпсилон-продукция

        # <Инициализаторы_продолжение>
        # Этот нетерминал обрабатывает хвост списка: ", <Выражение>, <Выражение> ..."
        table["<Инициализаторы_продолжение>"] = {
            TokenType.COMMA: [TokenType.COMMA, "<Выражение>", "<Инициализаторы_продолжение>"]
        }
        # Эпсилон-продукция, когда список заканчивается (т.е. следующий токен RCURLY)
        table["<Инициализаторы_продолжение>"][TokenType.RCURLY] = []
        # Если после запятой или в начале списка элементов нет других токенов, кроме RCURLY,
        # это будет обработано как синтаксическая ошибка (отсутствие правила).

        # <Альтернативное действие_extended>
        table["<Альтернативное действие_extended>"] = {
            TokenType.ELSE: [TokenType.ELSE, "<start_else_block>", "<Блок>", "<end_if_block>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.ELSE:
                 table["<Альтернативное действие_extended>"].setdefault(token_type, ["<end_if_block>"])

        # <Блок>
        table["<Блок>"] = {
            TokenType.LCURLY: [TokenType.LCURLY, "<Список операторов>", TokenType.RCURLY]
        }
        
        # <Логическое выражение>
        # Определяет порядок разбора операций: арифметические -> сравнения -> равенство -> И -> ИЛИ
        table["<Логическое выражение>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<ЛогическоеИ*>", "<ЛогическоеВыражение*>"],
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>",  # Сохраняем токен перед разбором
                TokenType.IDENTIFIER, 
                "<ФакторIdent>", 
                "<Терм*>", 
                "<Выражение*>", 
                "<Сравнение*>", 
                "<Проверка равенства*>", 
                "<ЛогическоеИ*>", 
                "<ЛогическоеВыражение*>"
            ],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<ЛогическоеИ*>", "<ЛогическоеВыражение*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<ЛогическоеИ*>", "<ЛогическоеВыражение*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<ЛогическоеИ*>", "<ЛогическоеВыражение*>"],
        }
        
        # <Логическое выражение*>
        table["<Логическое выражение*>"] = {
            TokenType.OR: ["|", "<Логическое И>", "<Логическое выражение*>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.OR:
                table["<Логическое выражение*>"][token_type] = []
        
        # <Логическое И>
        table["<Логическое И>"] = {
            TokenType.UNARY_MINUS: ["~", "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.IDENTIFIER: ["идентификатор", "<ФакторIdent>", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.INTEGER_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.FLOAT_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.LPAREN: ["(", "<Логическое выражение>", ")", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"]
        }

        # <Логическое И*>_wrapper and <Логическое И*>
        table["<ЛогическоеИ*_wrapper>"] = { 
            token_type: ["<Логическое И>", "<Логическое И*>"] for token_type in TokenType 
        }
        table["<Логическое И*>"] = {
            TokenType.AND: ["&", "<Проверка равенства>", "<Логическое И*>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.AND:
                 table["<Логическое И*>"].setdefault(token_type, [])
        
        # <ОператорDTIdent>
        table["<ОператорDTIdent>"] = {
            TokenType.ASSIGN: [TokenType.ASSIGN, "<Выражение>", "<gen_assign_op>"],
            TokenType.LSQUARE: [TokenType.LSQUARE, TokenType.INTEGER_CONST, TokenType.RSQUARE, TokenType.ASSIGN, "<Выражение>", "<gen_array_assign_op>"], # Для type arr[size] = expr;
        }
        explicitly_defined_for_op_dt_ident = list(table["<ОператорDTIdent>"].keys())
        for token_type in TokenType:
            if token_type not in explicitly_defined_for_op_dt_ident:
                table["<ОператорDTIdent>"][token_type] = []  # Пустая продукция для простых объявлений

        # <ПрисваиваниеIdent>
        table["<ПрисваиваниеIdent>"] = {
            TokenType.ASSIGN: ["<add_identifier_to_rpn_for_assign>", TokenType.ASSIGN, "<Выражение>", "<gen_assign_op>"],
            TokenType.LSQUARE: ["<add_identifier_to_rpn_for_assign>", TokenType.LSQUARE, "<Логическое выражение>", TokenType.RSQUARE, TokenType.ASSIGN, "<Выражение>", "<gen_array_assign_op>"]
        }
        
        # <Выражение>
        table["<Выражение>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>"],
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>",  # Сохраняем токен перед разбором
                TokenType.IDENTIFIER, 
                "<ФакторIdent>", 
                "<Терм*>", 
                "<Выражение*>"
            ],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>", "<Выражение*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>", "<Выражение*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>", "<Выражение*>"],
            TokenType.LCURLY: [TokenType.LCURLY, "<Инициализаторы>", TokenType.RCURLY]
        }
        
        # <Выражение*>
        table["<Выражение*>"] = {
            TokenType.PLUS: [TokenType.PLUS, "<Терм>", "<gen_op_plus>", "<Выражение*>"], # <gen_op_plus> уже был
            TokenType.MINUS: [TokenType.MINUS, "<Терм>", "<gen_op_minus>", "<Выражение*>"]
        }
        for token_type in TokenType:
            if token_type not in [TokenType.PLUS, TokenType.MINUS]:
                table["<Выражение*>"][token_type] = []
        
        # <Терм>
        table["<Терм>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>"],
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>",  # Сохраняем токен перед разбором
                TokenType.IDENTIFIER, 
                "<ФакторIdent>", 
                "<Терм*>"
            ],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>"]
        }
        
        # <Терм*>
        table["<Терм*>"] = {
            TokenType.MULTIPLY: [TokenType.MULTIPLY, "<Фактор>", "<gen_op_multiply>", "<Терм*>"],
            TokenType.DIVIDE: [TokenType.DIVIDE, "<Фактор>", "<gen_op_divide>", "<Терм*>"],
        }
        for token_type in TokenType:
            if token_type not in [TokenType.MULTIPLY, TokenType.DIVIDE]:
                table["<Терм*>"][token_type] = []
        
        # <Фактор>
        table["<Фактор>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<gen_op_uminus>"],
            # IDENTIFIER может быть простой переменной или началом доступа к массиву
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>", # Сохраняем токен идентификатора ДО его обработки
                TokenType.IDENTIFIER, 
                "<ФакторIdent>",                 # Обрабатываем возможное '[expr]'
                "<add_factor_to_rpn_if_not_array>" # Добавляем идентификатор в ОПЗ, если это была не операция доступа к массиву
            ],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST], # Уже добавляется в RPN при match
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST],   # Уже добавляется в RPN при match
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN]
        }
        
        # <ФакторIdent>
        table["<ФакторIdent>"] = {
            # Если за IDENTIFIER следует LSQUARE, это доступ к элементу массива
            TokenType.LSQUARE: [
                "<add_array_name_to_rpn>",  # Добавляем имя массива в RPN
                TokenType.LSQUARE, 
                "<Логическое выражение>", # Выражение для индекса
                TokenType.RSQUARE, 
                "<gen_array_access_op>"  # Семантическое действие для генерации ОПЗ доступа к массиву
            ]
        }
        # Эпсилон-продукции для <ФакторIdent> (если это не доступ к массиву)
        # Добавляем все токены, которые могут следовать за фактором в выражении
        follow_factor_ident = [
            TokenType.MULTIPLY, TokenType.DIVIDE, # Терм*
            TokenType.PLUS, TokenType.MINUS,      # Выражение*
            TokenType.LT, TokenType.GT, TokenType.EQ, TokenType.NEQ, # Сравнение*, ПроверкаРавенства*
            TokenType.AND, TokenType.OR,          # ЛогическоеИ*, ЛогическоеВыражение*
            TokenType.RPAREN, TokenType.SEMICOLON, TokenType.RSQUARE, TokenType.COMMA, 
            TokenType.RCURLY, TokenType.EOF # Добавим RCURLY для инициализаторов
        ]
        for token_type in follow_factor_ident:
            if token_type not in table["<ФакторIdent>"]: # Избегаем перезаписи правила для LSQUARE
                table["<ФакторIdent>"][token_type] = ["<add_factor_to_rpn_if_not_array>"] # Добавляем идентификатор в RPN при эпсилон-продукции
        
        # <ВводInput>
        table["<ВводInput>"] = {
            TokenType.IDENTIFIER: ["<save_identifier_token>", TokenType.IDENTIFIER, "<ВводInputIdent>", TokenType.SEMICOLON]
        }
        
        # <ВводInputIdent>
        table["<ВводInputIdent>"] = {
            TokenType.LSQUARE: ["<add_input_identifier_to_rpn>", TokenType.LSQUARE, "<Логическое выражение>", TokenType.RSQUARE, "<gen_input_array_op>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.LSQUARE:
                table["<ВводInputIdent>"][token_type] = ["<add_input_identifier_to_rpn>", "<gen_input_op>"]  # Для простых переменных
        
        # <Сравнение>
        table["<Сравнение>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>"],
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>",  # Сохраняем токен перед разбором
                TokenType.IDENTIFIER, 
                "<ФакторIdent>", 
                "<Терм*>", 
                "<Выражение*>"
            ],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>", "<Выражение*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>", "<Выражение*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>", "<Выражение*>"],
        }

        # <Сравнение*> (обрабатывает <, >)
        # Операнд для <, > - это <Выражение> (арифметическое)
        table["<Сравнение*>"] = {
            TokenType.LT: [TokenType.LT, "<Выражение>", "<gen_op_lt>", "<Сравнение*>"],
            TokenType.GT: [TokenType.GT, "<Выражение>", "<gen_op_gt>", "<Сравнение*>"],
            # Добавим LE, GE если они есть
        }
        follow_sravnenie_star = [
            TokenType.EQ, TokenType.NEQ, TokenType.AND, TokenType.OR, 
            TokenType.RPAREN, TokenType.SEMICOLON, TokenType.LCURLY, 
            TokenType.RSQUARE, TokenType.COMMA, TokenType.EOF
        ]
        for token_type in follow_sravnenie_star:
            if token_type not in table["<Сравнение*>"]:
                 table["<Сравнение*>"][token_type] = []
        
        # <Проверка равенства*> (обрабатывает ?, !)
        # Операнд для ?, ! - это <Выражение><Сравнение*>
        table["<Проверка равенства*>"] = {
            TokenType.EQ: [TokenType.EQ, "<Выражение>", "<Сравнение*>", "<gen_op_eq>", "<Проверка равенства*>"],
            TokenType.NEQ: [TokenType.NEQ, "<Выражение>", "<Сравнение*>", "<gen_op_neq>", "<Проверка равенства*>"], # Добавим NEQ позже
        }
        follow_proverka_ravenstva_star = [
            TokenType.AND, TokenType.OR, TokenType.RPAREN, TokenType.SEMICOLON, 
            TokenType.LCURLY, TokenType.RSQUARE, TokenType.COMMA, TokenType.EOF
        ]
        for token_type in follow_proverka_ravenstva_star:
            if token_type not in table["<Проверка равенства*>"]:
                 table["<Проверка равенства*>"][token_type] = []

        # <ЛогическоеИ*> (обрабатывает &)
        # Операнд для & - это <Выражение><Сравнение*><Проверка равенства*>
        table["<ЛогическоеИ*>"] = {
            TokenType.AND: [TokenType.AND, "<Выражение>", "<Сравнение*>", "<Проверка равенства*>", "<gen_op_and>", "<ЛогическоеИ*>"],
        }
        follow_logicheskoe_i_star = [
            TokenType.OR, TokenType.RPAREN, TokenType.SEMICOLON, 
            TokenType.LCURLY, TokenType.RSQUARE, TokenType.COMMA, TokenType.EOF
        ]
        for token_type in follow_logicheskoe_i_star:
            if token_type not in table["<ЛогическоеИ*>"]:
                 table["<ЛогическоеИ*>"][token_type] = []

        # <ЛогическоеВыражение*> (обрабатывает |)
        # Операнд для | - это <Выражение><Сравнение*><Проверка равенства*><ЛогическоеИ*>
        table["<ЛогическоеВыражение*>"] = {
            TokenType.OR: [TokenType.OR, "<Выражение>", "<Сравнение*>", "<Проверка равенства*>", "<ЛогическоеИ*>", "<gen_op_or>", "<ЛогическоеВыражение*>"],
        }
        follow_logicheskoe_virazhenie_star = [
            TokenType.RPAREN, TokenType.SEMICOLON, TokenType.LCURLY, 
            TokenType.RSQUARE, TokenType.COMMA, TokenType.EOF
        ]
        for token_type in follow_logicheskoe_virazhenie_star:
            if token_type not in table["<ЛогическоеВыражение*>"]:
                 table["<ЛогическоеВыражение*>"][token_type] = []

        # Определение для <Инициализаторы> и <Инициализаторы_продолжение>
        # FIRST(<ЛогВыражение>) уже определен как first_arith_expr
        first_arith_expr = {TokenType.UNARY_MINUS, TokenType.IDENTIFIER, TokenType.INTEGER_CONST, TokenType.FLOAT_CONST, TokenType.LPAREN, TokenType.LCURLY}

        # Определяем токены, которые могут начинать <Выражение>
        # Основываясь на существующем определении table["<Выражение>"]
        first_expression_starters = {
            TokenType.UNARY_MINUS, TokenType.IDENTIFIER, TokenType.INTEGER_CONST,
            TokenType.FLOAT_CONST, TokenType.LPAREN, TokenType.LCURLY
        }

        # Корректное определение для <Инициализаторы>
        # <Инициализаторы> ::= <Выражение> <Инициализаторы_продолжение> | epsilon (если RCURLY)
        table["<Инициализаторы>"] = {}
        for token_type in first_expression_starters:
            # Если токен может начать <Выражение>, то он может начать список инициализаторов
            table["<Инициализаторы>"][token_type] = ["<Выражение>", "<Инициализаторы_продолжение>"]
        # Эпсилон-продукция для пустого списка {} или когда список уже разобран <Инициализаторы_продолжение>
        table["<Инициализаторы>"][TokenType.RCURLY] = []

        # Новый нетерминал <Инициализаторы_продолжение>
        # <Инициализаторы_продолжение> ::= COMMA <Выражение> <Инициализаторы_продолжение> | epsilon (если RCURLY)
        table["<Инициализаторы_продолжение>"] = {
            TokenType.COMMA: [TokenType.COMMA, "<Выражение>", "<Инициализаторы_продолжение>"],
            TokenType.RCURLY: []  # Эпсилон-продукция, если достигнут конец списка
        }

        # Удаляем старое правило <Инициализаторы*>, если оно существует и конфликтует
        if "<Инициализаторы*>" in table:
            # Сначала убедимся, что это не то же самое, что мы только что определили
            # (маловероятно из-за другого имени и структуры)
            # Это безопасно, если <Инициализаторы*> - это старое, неправильное правило.
            del table["<Инициализаторы*>"]
        
        # Правило в <Выражение>, использующее <Инициализаторы>, должно оставаться:
        # table["<Выражение>"][TokenType.LCURLY] = [TokenType.LCURLY, "<Инициализаторы>", TokenType.RCURLY]
        # Убедитесь, что оно присутствует и использует именно "<Инициализаторы>".
        # Судя по вашему коду, оно уже есть:
        # table["<Выражение"] = {
        #     ...
        #     TokenType.LCURLY: [TokenType.LCURLY, "<Инициализаторы>", TokenType.RCURLY]
        #     ...
        # }

        # ... остальные правила ...

        return table

    def execute_semantic_action(self, action, current_token_arg): # Renamed current_token to current_token_arg to avoid conflict
        """
        Выполняет семантическое действие на основе маркера.
        """
        # print(f"Семантическое действие: {action} для токена {current_token_arg}")

        if action == "<push_int_type>":
            self.data_types_stack.append("int")
        elif action == "<push_float_type>":
            self.data_types_stack.append("float")
        elif action == "<save_identifier_token>":
            if self.current_index < len(self.tokens):
                 self.context["last_identifier_token"] = self.tokens[self.current_index]
            else:
                self.error("Internal parser error: <save_identifier_token> called at end of tokens.")

        elif action == "<add_variable_declaration>":
            var_token = self.context.get("last_identifier_token")
            if not var_token or var_token.token_type != TokenType.IDENTIFIER:
                self.error("Internal parser error: last_identifier_token not set correctly for variable declaration.")
                return

            var_name = var_token.value
            if not self.data_types_stack:
                self.error(f"Internal parser error: data_types_stack is empty for variable {var_name}.")
                return
            var_type = self.data_types_stack.pop()
            
            self.symbol_table.add_symbol(var_name, var_type, var_token.line, var_token.position, is_array=False)
            self.context["last_identifier_token"] = None

        elif action == "<add_dynamic_array_declaration>":
            arr_token = self.context.get("last_identifier_token")
            if not arr_token or arr_token.token_type != TokenType.IDENTIFIER:
                self.error("Internal parser error: last_identifier_token not set correctly for dynamic array declaration.")
                return

            arr_name = arr_token.value
            if not self.data_types_stack:
                self.error(f"Internal parser error: data_types_stack is empty for array {arr_name}.")
                return
            arr_type = self.data_types_stack.pop() 

            self.symbol_table.add_symbol(arr_name, arr_type, arr_token.line, arr_token.position, is_array=True)
            # Для динамического массива размер уже находится в RPN (из <Выражение>)
            # Сначала добавляем имя массива, потом команду DECL_ARR
            # Порядок на стеке должен быть: [..., arr_name, size] для DECL_ARR
            self.rpn_generator.add_identifier(arr_name)
            self.rpn_generator.add_operator('DECL_ARR')
            self.context["last_identifier_token"] = None

        elif action == "<add_array_declaration>":
            arr_token = self.context.get("last_identifier_token")
            if not arr_token or arr_token.token_type != TokenType.IDENTIFIER:
                self.error("Internal parser error: last_identifier_token not set correctly for array declaration.")
                return

            arr_name = arr_token.value
            if not self.data_types_stack:
                self.error(f"Internal parser error: data_types_stack is empty for array {arr_name}.")
                return
            arr_type = self.data_types_stack.pop() 

            self.symbol_table.add_symbol(arr_name, arr_type, arr_token.line, arr_token.position, is_array=True)
            self.rpn_generator.add_array_declaration(arr_name)
            self.context["last_identifier_token"] = None

        elif action == "<gen_op_plus>":
            self.rpn_generator.add_operator('+')
        elif action == "<gen_op_minus>":
            self.rpn_generator.add_operator('-')
        elif action == "<gen_op_uminus>":
            self.rpn_generator.add_operator('~')
        elif action == "<gen_op_multiply>":
            self.rpn_generator.add_operator('*')
        elif action == "<gen_op_divide>":
            self.rpn_generator.add_operator('/')
        elif action == "<gen_op_lt>":
            self.rpn_generator.add_operator('<')
        elif action == "<gen_op_gt>":
            self.rpn_generator.add_operator('>')
        elif action == "<gen_op_neq>":
            self.rpn_generator.add_operator('!')
        elif action == "<gen_op_and>":
            self.rpn_generator.add_operator('&')
        elif action == "<gen_op_or>":
            self.rpn_generator.add_operator('|')
        elif action == "<save_current_token_as_factor>":
            # Сохраняем текущий токен идентификатора для возможного использования в факторе
            if self.current_index < len(self.tokens):
                self.context["saved_factor_token"] = self.tokens[self.current_index]
            else:
                self.error("Internal parser error: <save_current_token_as_factor> called at end of tokens.")
        elif action == "<add_factor_to_rpn_if_not_array>":
            # Добавляем идентификатор в ОПС только если это не был доступ к массиву
            saved_token = self.context.get("saved_factor_token")
            if saved_token and saved_token.token_type == TokenType.IDENTIFIER:
                # print(f"DEBUG: Adding factor to RPN: {saved_token.value}")  # Отладка
                self.rpn_generator.add_identifier(saved_token.value)
                self.context["saved_factor_token"] = None
        elif action == "<gen_assign_op>":
            # Генерируем операцию присваивания
            self.rpn_generator.add_operator('=')
        elif action == "<gen_array_assign_op>":
            # Генерируем операцию присваивания для массива
            self.rpn_generator.add_operator('array_assign')  # Специальная операция для присваивания массиву
        elif action == "<gen_output_op>":
            # Генерируем операцию вывода
            self.rpn_generator.add_operator('w')
        elif action == "<add_identifier_to_rpn_for_assign>":
            # Добавляем идентификатор переменной в RPN для присваивания
            var_token = self.context.get("last_identifier_token")
            if var_token and var_token.token_type == TokenType.IDENTIFIER:
                self.rpn_generator.add_identifier(var_token.value)
        elif action == "<add_input_identifier_to_rpn>":
            # Добавляем идентификатор переменной в RPN для операции ввода
            var_token = self.context.get("last_identifier_token")
            if var_token and var_token.token_type == TokenType.IDENTIFIER:
                self.rpn_generator.add_identifier(var_token.value)
        elif action == "<gen_input_op>":
            # Генерируем операцию ввода
            self.rpn_generator.add_operator('r')
        elif action == "<gen_input_array_op>":
            # Генерируем операцию ввода в массив
            # Стек: [array_name, index_expr]
            # Нужно: прочитать значение, затем присвоить arr[index] = value
            self.rpn_generator.add_operator('r_array')  # Специальная операция для ввода в массив
        elif action == "<gen_array_access_op>":
            # Генерируем операцию доступа к элементу массива
            # Стек: [array_name, index_expr]
            # Нужно: получить arr[index]
            self.rpn_generator.add_operator('array_index')  # Операция индексирования массива
        elif action == "<add_array_name_to_rpn>":
            # Добавляем имя массива в RPN для доступа к элементу
            saved_token = self.context.get("saved_factor_token")
            if saved_token and saved_token.token_type == TokenType.IDENTIFIER:
                self.rpn_generator.add_identifier(saved_token.value)
                self.context["saved_factor_token"] = None  # Очищаем, чтобы <add_factor_to_rpn_if_not_array> не добавил снова
        elif action == "<while>":
            # Сохраняем позицию начала цикла while
            loop_start = len(self.rpn_generator.rpn)  # Текущая длина RPN = следующий индекс
            if "while_stack" not in self.context:
                self.context["while_stack"] = []
            self.context["while_stack"].append({"start": loop_start})
        elif action == "<after_while_condition>":
            # После обработки условия добавляем условный переход $JF
            # Если условие ложно, переходим в конец цикла (адрес пока неизвестен)
            if "while_stack" not in self.context or not self.context["while_stack"]:
                raise ValueError("while_stack is empty in <after_while_condition>")
            
            # Добавляем $JF и placeholder для адреса
            self.rpn_generator.add_operator('$JF')
            jf_address_index = len(self.rpn_generator.rpn)  # Позиция для адреса
            self.rpn_generator.rpn.append(None)  # Placeholder для адреса перехода
            
            # Сохраняем позицию, куда нужно будет записать адрес
            self.context["while_stack"][-1]["jf_address_index"] = jf_address_index
        elif action == "<end_while_block>":
            # В конце блока while добавляем безусловный переход к началу цикла
            if "while_stack" not in self.context or not self.context["while_stack"]:
                raise ValueError("while_stack is empty in <end_while_block>")
            
            while_info = self.context["while_stack"].pop()
            loop_start = while_info["start"]
            jf_address_index = while_info["jf_address_index"]
            
            # Добавляем безусловный переход к началу цикла
            self.rpn_generator.add_operator('$J')
            self.rpn_generator.rpn.append(loop_start)
            
            # Записываем адрес после цикла в placeholder для $JF
            end_address = len(self.rpn_generator.rpn)  # Адрес ПОСЛЕ добавления $J
            self.rpn_generator.rpn[jf_address_index] = end_address
        
        pass


    def parse(self):
        self.parse_table = self.build_parse_table()
        
        while self.stack:
            top_of_stack = self.stack[-1]
            # current_token variable is defined here and shadows the argument if it had the same name
            current_token_loop = self.current_token() 

            # print(f\\"Стек: {self.stack}\\")
            # print(f\\"Текущий токен: {current_token_loop}\\")

            if top_of_stack == TokenType.EOF and current_token_loop.token_type == TokenType.EOF:
                # print(\\"Разбор успешно завершен.\\")
                break

            if isinstance(top_of_stack, TokenType) and top_of_stack == current_token_loop.token_type:
                self.stack.pop()
                # Добавляем константы в ОПЗ здесь
                if top_of_stack == TokenType.INTEGER_CONST or top_of_stack == TokenType.FLOAT_CONST:
                    self.rpn_generator.add_constant(current_token_loop.value)
                # Идентификаторы как операнды теперь обрабатываются через семантические действия в правилах (<add_factor_to_rpn_if_not_array>)
                # Старый 'pass' для TokenType.IDENTIFIER здесь был правильным, т.к. обработка зависит от контекста правила.
                
                self.advance()
            elif isinstance(top_of_stack, str) and top_of_stack.startswith("<") and top_of_stack.endswith(">") and (
                 not top_of_stack.startswith("<gen_") and not top_of_stack.startswith("<after_") and
                 not top_of_stack.startswith("<end_") and not top_of_stack.startswith("<start_") and
                 not top_of_stack.startswith("<while") and not top_of_stack.startswith("<push_") and
                 not top_of_stack.startswith("<save_") and not top_of_stack.startswith("<add_")): # Non-terminal
                
                rule = self.parse_table.get(top_of_stack, {}).get(current_token_loop.token_type)
                if rule is None:
                    expected_tokens = list(self.parse_table.get(top_of_stack, {}).keys())
                    self.error(f"Ожидался один из токенов {expected_tokens} или правило для нетерминала '{top_of_stack}' не найдено для токена {current_token_loop.token_type}, но получен {current_token_loop.token_type} ('{current_token_loop.value}')")
                    break 
                
                self.stack.pop()
                for symbol in reversed(rule):
                    self.stack.append(symbol)
            elif isinstance(top_of_stack, str) and (top_of_stack.startswith("<gen_") or top_of_stack.startswith("<after_") or top_of_stack.startswith("<end_") or top_of_stack.startswith("<start_") or top_of_stack.startswith("<while") or top_of_stack.startswith("<push_") or top_of_stack.startswith("<save_") or top_of_stack.startswith("<add_")): # Semantic action
                action_to_execute = self.stack.pop()
                # Pass current_token_loop (local to parse loop) to semantic actions
                self.execute_semantic_action(action_to_execute, current_token_loop) 
            else: 
                self.error(f"Несоответствие токена. Ожидался {top_of_stack}, но получен {current_token_loop.token_type} ('{current_token_loop.value}') или неизвестный символ в стеке.")
                break
        
        # print(f\\"Финальная RPN: {self.rpn_generator.rpn}\\")
        # print(f\\"Таблица символов: {self.symbol_table.symbols}\\")
        return self.rpn_generator.rpn, self.symbol_table