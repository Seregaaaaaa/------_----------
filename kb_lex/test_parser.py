import sys
from src.lexer import analyze
from src.parser import Parser

def run_parser_test(filename):

    with open(filename, 'r', encoding='utf-8') as file:
        source_code = file.read()
    
    print(f"\nАнализ файла: {filename}")
    print("=" * 50)
    
    tokens = analyze(source_code)
    
    print("\nРезультаты лексического анализа:")
    print("-" * 50)
    for token in tokens:
        value_str = f" = {token.value}" if token.value else ""
        print(f"Строка {token.line}, позиция {token.position}: {token.token_type.name}{value_str}")
    
    parser = Parser(tokens)
    
    try:
        rpn = parser.parse()
        
        print("\nРезультаты синтаксического анализа (ОПС):")
        print("-" * 50)
        print('RPN:', ' '.join(list(map(str, rpn[0]))))
        #for i, j in enumerate(rpn[0]):
        #    print(i, j)
        #print('SymbolTable: ', rpn[1])
        
        print("\nАнализ успешно завершен!")
        return True
    except Exception as e:
        print(f"\nОшибка при синтаксическом анализе: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python test_parser.py <путь_к_файлу>")
        sys.exit(1)
        
    test_file = sys.argv[1]
    success = run_parser_test(test_file)
    sys.exit(0 if success else 1)
