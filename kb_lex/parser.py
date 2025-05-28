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
        
        table["<Программа>"] = {
            TokenType.INT: ["<push_int_type>", TokenType.INT, "<ОператорDT>", "<Список операторов>"],
            TokenType.FLOAT: ["<push_float_type>", TokenType.FLOAT, "<ОператорDT>", "<Список операторов>"],
            TokenType.IF: [TokenType.IF, TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<after_if_condition>", "<Блок>", "<Альтернативное действие_extended>", "<Список операторов>"],
            TokenType.IDENTIFIER: ["<save_identifier_token>", TokenType.IDENTIFIER, "<ПрисваиваниеIdent>", TokenType.SEMICOLON, "<Список операторов>"],
            TokenType.WHILE: [TokenType.WHILE, "<while>", TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<after_while_condition>", "<Блок>", "<end_while_block>", "<Список операторов>"],
            TokenType.INPUT: [TokenType.INPUT, "<ВводInput>", "<Список операторов>"],
            TokenType.OUTPUT: [TokenType.OUTPUT, "<Логическое выражение>", "<gen_output_op>", TokenType.SEMICOLON, "<Список операторов>"]
        }
        
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
        
        table["<ОператорDT_array>"] = {
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

        table["<Инициализаторы>"] = {}
        expression_starter_tokens = [
            TokenType.UNARY_MINUS, TokenType.IDENTIFIER, TokenType.INTEGER_CONST,
            TokenType.FLOAT_CONST, TokenType.LPAREN, TokenType.LCURLY
        ]
        for token_type in expression_starter_tokens:
            table["<Инициализаторы>"][token_type] = ["<Выражение>", "<Инициализаторы_продолжение>"]
        
        table["<Инициализаторы>"][TokenType.RCURLY] = [] 

        table["<Инициализаторы_продолжение>"] = {
            TokenType.COMMA: [TokenType.COMMA, "<Выражение>", "<Инициализаторы_продолжение>"]
        }
        table["<Инициализаторы_продолжение>"][TokenType.RCURLY] = []

        table["<Альтернативное действие_extended>"] = {
            TokenType.ELSE: [TokenType.ELSE, "<start_else_block>", "<Блок>", "<end_if_block>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.ELSE:
                 table["<Альтернативное действие_extended>"].setdefault(token_type, ["<end_if_block>"])

        table["<Блок>"] = {
            TokenType.LCURLY: [TokenType.LCURLY, "<Список операторов>", TokenType.RCURLY]
        }
        

        table["<Логическое выражение>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*>", "<Проверка равенства*>", "<ЛогическоеИ*>", "<ЛогическоеВыражение*>"],
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>",  
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
        

        table["<Логическое выражение*>"] = {
            TokenType.OR: ["|", "<Логическое И>", "<Логическое выражение*>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.OR:
                table["<Логическое выражение*>"][token_type] = []
        

        table["<Логическое И>"] = {
            TokenType.UNARY_MINUS: ["~", "<Фактор>", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.IDENTIFIER: ["идентификатор", "<ФакторIdent>", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.INTEGER_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.FLOAT_CONST: ["константа", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"],
            TokenType.LPAREN: ["(", "<Логическое выражение>", ")", "<Терм*>", "<Выражение*>", "<Сравнение*_wrapper>", "<ПроверкаРавенства*_wrapper>", "<Логическое И*>"]
        }


        table["<ЛогическоеИ*_wrapper>"] = { 
            token_type: ["<Логическое И>", "<Логическое И*>"] for token_type in TokenType 
        }
        table["<Логическое И*>"] = {
            TokenType.AND: ["&", "<Проверка равенства>", "<Логическое И*>"]
        }
        for token_type in TokenType:
            if token_type != TokenType.AND:
                 table["<Логическое И*>"].setdefault(token_type, [])
        

        table["<ОператорDTIdent>"] = {
            TokenType.ASSIGN: [TokenType.ASSIGN, "<Выражение>", "<gen_assign_op>"],
            TokenType.LSQUARE: [TokenType.LSQUARE, TokenType.INTEGER_CONST, TokenType.RSQUARE, TokenType.ASSIGN, "<Выражение>", "<gen_array_assign_op>"], # Для type arr[size] = expr;
        }
        explicitly_defined_for_op_dt_ident = list(table["<ОператорDTIdent>"].keys())
        for token_type in TokenType:
            if token_type not in explicitly_defined_for_op_dt_ident:
                table["<ОператорDTIdent>"][token_type] = []  

        table["<ПрисваиваниеIdent>"] = {
            TokenType.ASSIGN: ["<add_identifier_to_rpn_for_assign>", TokenType.ASSIGN, "<Выражение>", "<gen_assign_op>"],
            TokenType.LSQUARE: ["<add_identifier_to_rpn_for_assign>", TokenType.LSQUARE, "<Логическое выражение>", TokenType.RSQUARE, TokenType.ASSIGN, "<Выражение>", "<gen_array_assign_op>"]
        }
        

        table["<Выражение>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>", "<Выражение*>"],
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>",  
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
        
        table["<Выражение*>"] = {
            TokenType.PLUS: [TokenType.PLUS, "<Терм>", "<gen_op_plus>", "<Выражение*>"], # <gen_op_plus> уже был
            TokenType.MINUS: [TokenType.MINUS, "<Терм>", "<gen_op_minus>", "<Выражение*>"]
        }
        for token_type in TokenType:
            if token_type not in [TokenType.PLUS, TokenType.MINUS]:
                table["<Выражение*>"][token_type] = []
        

        table["<Терм>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<Терм*>"],
            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>",  
                TokenType.IDENTIFIER, 
                "<ФакторIdent>", 
                "<Терм*>"
            ],
            TokenType.INTEGER_CONST: [TokenType.INTEGER_CONST, "<Терм*>"],
            TokenType.FLOAT_CONST: [TokenType.FLOAT_CONST, "<Терм*>"],
            TokenType.LPAREN: [TokenType.LPAREN, "<Логическое выражение>", TokenType.RPAREN, "<Терм*>"]
        }
        

        table["<Терм*>"] = {
            TokenType.MULTIPLY: [TokenType.MULTIPLY, "<Фактор>", "<gen_op_multiply>", "<Терм*>"],
            TokenType.DIVIDE: [TokenType.DIVIDE, "<Фактор>", "<gen_op_divide>", "<Терм*>"],
        }
        for token_type in TokenType:
            if token_type not in [TokenType.MULTIPLY, TokenType.DIVIDE]:
                table["<Терм*>"][token_type] = []
        

        table["<Фактор>"] = {
            TokenType.UNARY_MINUS: [TokenType.UNARY_MINUS, "<Фактор>", "<gen_op_uminus>"],

            TokenType.IDENTIFIER: [
                "<save_current_token_as_factor>", 
                TokenType.IDENTIFIER, 
                "<ФакторIdent>",
                "<add_factor_to_rpn_if_not_array>" 
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


        first_expression_starters = {
            TokenType.UNARY_MINUS, TokenType.IDENTIFIER, TokenType.INTEGER_CONST,
            TokenType.FLOAT_CONST, TokenType.LPAREN, TokenType.LCURLY
        }

        table["<Инициализаторы>"] = {}
        for token_type in first_expression_starters:

            table["<Инициализаторы>"][token_type] = ["<Выражение>", "<Инициализаторы_продолжение>"]

        table["<Инициализаторы>"][TokenType.RCURLY] = []


        table["<Инициализаторы_продолжение>"] = {
            TokenType.COMMA: [TokenType.COMMA, "<Выражение>", "<Инициализаторы_продолжение>"],
            TokenType.RCURLY: []  
        }

        
        if "<Инициализаторы*>" in table:

            del table["<Инициализаторы*>"]


        return table

    def execute_semantic_action(self, action, current_token_arg): 
        """
        Выполняет семантическое действие на основе маркера.
        """


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

            if self.current_index < len(self.tokens):
                self.context["saved_factor_token"] = self.tokens[self.current_index]
            else:
                self.error("Internal parser error: <save_current_token_as_factor> called at end of tokens.")
        elif action == "<add_factor_to_rpn_if_not_array>":

            saved_token = self.context.get("saved_factor_token")
            if saved_token and saved_token.token_type == TokenType.IDENTIFIER:

                self.rpn_generator.add_identifier(saved_token.value)
                self.context["saved_factor_token"] = None
        elif action == "<gen_assign_op>":
            self.rpn_generator.add_operator('=')
        elif action == "<gen_array_assign_op>":
            self.rpn_generator.add_operator('array_assign')  
        elif action == "<gen_output_op>":

            self.rpn_generator.add_operator('w')
        elif action == "<add_identifier_to_rpn_for_assign>":

            var_token = self.context.get("last_identifier_token")
            if var_token and var_token.token_type == TokenType.IDENTIFIER:
                self.rpn_generator.add_identifier(var_token.value)
        elif action == "<add_input_identifier_to_rpn>":

            var_token = self.context.get("last_identifier_token")
            if var_token and var_token.token_type == TokenType.IDENTIFIER:
                self.rpn_generator.add_identifier(var_token.value)
        elif action == "<gen_input_op>":
            self.rpn_generator.add_operator('r')
        elif action == "<gen_input_array_op>":

            self.rpn_generator.add_operator('r_array')  
        elif action == "<gen_array_access_op>":

            self.rpn_generator.add_operator('array_index')  
        elif action == "<add_array_name_to_rpn>":
            saved_token = self.context.get("saved_factor_token")
            if saved_token and saved_token.token_type == TokenType.IDENTIFIER:
                self.rpn_generator.add_identifier(saved_token.value)
                self.context["saved_factor_token"] = None  
        elif action == "<while>":
            loop_start = len(self.rpn_generator.rpn)  
            if "while_stack" not in self.context:
                self.context["while_stack"] = []
            self.context["while_stack"].append({"start": loop_start})
        elif action == "<after_while_condition>":
            if "while_stack" not in self.context or not self.context["while_stack"]:
                raise ValueError("while_stack is empty in <after_while_condition>")
            
            self.rpn_generator.add_operator('$JF')
            jf_address_index = len(self.rpn_generator.rpn)
            self.rpn_generator.rpn.append(None)  
            
            self.context["while_stack"][-1]["jf_address_index"] = jf_address_index
        elif action == "<end_while_block>":
            if "while_stack" not in self.context or not self.context["while_stack"]:
                raise ValueError("while_stack is empty in <end_while_block>")
            
            while_info = self.context["while_stack"].pop()
            loop_start = while_info["start"]
            jf_address_index = while_info["jf_address_index"]
            
            self.rpn_generator.add_operator('$J')
            self.rpn_generator.rpn.append(loop_start)
            
            end_address = len(self.rpn_generator.rpn)  
            self.rpn_generator.rpn[jf_address_index] = end_address
        
        # Семантические действия для if-else конструкций
        elif action == "<after_if_condition>":
            # Программа 9: После условия if
            # Добавляем условный переход $JF с заполнителем
            self.rpn_generator.add_operator('$JF')
            jf_address_index = len(self.rpn_generator.rpn)
            self.rpn_generator.rpn.append(None)  # Заполнитель для адреса
            
            # Инициализируем стек if-else, если его нет
            if "if_stack" not in self.context:
                self.context["if_stack"] = []
            
            # Сохраняем индекс команды $JF для последующего заполнения
            self.context["if_stack"].append({"jf_address_index": jf_address_index})
        
        elif action == "<start_else_block>":
            # Программа 11: Начало блока else
            if "if_stack" not in self.context or not self.context["if_stack"]:
                raise ValueError("if_stack is empty in <start_else_block>")
            
            if_info = self.context["if_stack"][-1]
            jf_address_index = if_info["jf_address_index"]
            
            # Добавляем безусловный переход $J для пропуска блока else
            self.rpn_generator.add_operator('$J')
            j_address_index = len(self.rpn_generator.rpn)
            self.rpn_generator.rpn.append(None)  # Заполнитель для адреса
            
            # Заполняем адрес для $JF (переход на начало блока else)
            current_address = len(self.rpn_generator.rpn)
            self.rpn_generator.rpn[jf_address_index] = current_address
            
            # Сохраняем индекс команды $J для последующего заполнения
            if_info["j_address_index"] = j_address_index
        
        elif action == "<end_if_block>":
            # Программа 10: Конец блока if (или if-else)
            if "if_stack" not in self.context or not self.context["if_stack"]:
                raise ValueError("if_stack is empty in <end_if_block>")
            
            if_info = self.context["if_stack"].pop()
            
            # Если есть $J (блок else), заполняем его адрес
            if "j_address_index" in if_info:
                j_address_index = if_info["j_address_index"]
                end_address = len(self.rpn_generator.rpn)
                self.rpn_generator.rpn[j_address_index] = end_address
            else:
                # Если нет блока else, заполняем адрес для $JF
                jf_address_index = if_info["jf_address_index"]
                end_address = len(self.rpn_generator.rpn)
                self.rpn_generator.rpn[jf_address_index] = end_address
        
        pass


    def parse(self):
        self.parse_table = self.build_parse_table()
        
        while self.stack:
            top_of_stack = self.stack[-1]
            current_token_loop = self.current_token() 


            if top_of_stack == TokenType.EOF and current_token_loop.token_type == TokenType.EOF:

                break

            if isinstance(top_of_stack, TokenType) and top_of_stack == current_token_loop.token_type:
                self.stack.pop()

                if top_of_stack == TokenType.INTEGER_CONST or top_of_stack == TokenType.FLOAT_CONST:
                    self.rpn_generator.add_constant(current_token_loop.value)

                
                self.advance()
            elif isinstance(top_of_stack, str) and top_of_stack.startswith("<") and top_of_stack.endswith(">") and (
                not top_of_stack.startswith("<gen_") and not top_of_stack.startswith("<after_") and
                not top_of_stack.startswith("<end_") and not top_of_stack.startswith("<start_") and
                not top_of_stack.startswith("<while") and not top_of_stack.startswith("<push_") and
                not top_of_stack.startswith("<save_") and not top_of_stack.startswith("<add_")): 
                
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

                self.execute_semantic_action(action_to_execute, current_token_loop) 
            else: 
                self.error(f"Несоответствие токена. Ожидался {top_of_stack}, но получен {current_token_loop.token_type} ('{current_token_loop.value}') или неизвестный символ в стеке.")
                break
        
        return self.rpn_generator.rpn, self.symbol_table