import sys
from src.lexer import analyze
from src.token_type import TokenType

def print_token_info(token):
    value_str = f" = {token.value}" if token.value else ""
    print(f"Строка {token.line}, позиция {token.position}: {token.token_type.name}{value_str}")

def run_lexer_test(filename):

    with open(filename, 'r', encoding='utf-8') as file:
        source_code = file.read()

    print(f"\nАнализ файла: {filename}")
    print("=" * 50)
    
    tokens = analyze(source_code)

    print("\nРезультаты лексического анализа:")
    print("-" * 50)
    
    for token in tokens:
        print_token_info(token)
        
    print("\nАнализ успешно завершен!")
    return True
    

if __name__ == "__main__":
    test_file = sys.argv[1]
    success = run_lexer_test(test_file)
    sys.exit(0 if success else 1)