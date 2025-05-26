import sys
import os

# Добавляем путь к родительскому каталогу, чтобы можно было импортировать src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.compiler import Compiler

def main():
    if len(sys.argv) < 2:
        print("Использование: python test_compiler.py <имя_файла> [входные_данные...]")
        print("Пример: python test_compiler.py test7.kb 3 1 2 3")
        print("Если входные данные не указаны, программа запросит их интерактивно.")
        sys.exit(1)

    filepath = sys.argv[1]
    input_values = []
    
    # Парсим входные данные из аргументов командной строки
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            try:
                input_values.append(int(arg))
            except ValueError:
                print(f"Ошибка: '{arg}' не является целым числом.")
                sys.exit(1)
        print(f"Используются предопределенные входные данные: {input_values}")
    else:
        print("Программа будет запрашивать входные данные интерактивно.")

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filepath}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла '{filepath}': {e}")
        sys.exit(1)

    compiler = Compiler()
    
    # Передаем входные данные в компилятор
    if input_values:
        compiler.set_input_values(input_values)

    print(f"--- Исходный код из файла '{filepath}' ---")
    print(source_code)
    print("-" * 30)

    try:
        # Компиляция и выполнение
        program_output, final_symbol_table = compiler.execute(source_code)

        # Получение результатов этапов
        tokens = compiler.get_tokens()
        rpn = compiler.get_rpn()

        print("--- Токены (Лексический анализ) ---")
        if tokens:
            for token in tokens:
                print(token)
        else:
            print("Нет токенов (возможно, пустой файл или ошибка лексера).")
        print("-" * 30)

        print("--- ОПЗ (Синтаксический анализ) ---")
        if rpn:
            for i, item in enumerate(rpn):
                print(f"{i}: {item}")
        else:
            print("ОПЗ не сгенерирована (возможно, ошибка синтаксического анализа).")
        print("-" * 30)
        
        if program_output is not None:
            print("--- Вывод программы (Интерпретация ОПЗ) ---")
            if program_output:
                for line in program_output:
                    print(line)
            else:
                print("(нет вывода)")
            print("-" * 30)

            print("--- Таблица символов после выполнения ---")
            if final_symbol_table:
                for var_name, value in final_symbol_table.items():
                    print(f"{var_name}: {value}")
            else:
                print("(пусто)")
            print("-" * 30)
        else:
            # Ошибка компиляции или выполнения уже должна была быть выведена
            # или перехвачена выше и вызвала бы sys.exit(1)
            # Этот блок может быть достигнут, если execute возвращает (None, None)
            # из-за ошибки, обработанной внутри Compiler.parse()
            print("Компиляция или выполнение не удалось. Подробности см. выше.")
            sys.exit(1)


    except Exception as e:
        print(f"Произошла ошибка во время компиляции или выполнения: {e}")
        # Дополнительно выведем токены и ОПЗ, если они успели сгенерироваться
        tokens = compiler.get_tokens()
        rpn = compiler.get_rpn()
        if tokens:
            print("\\n--- Токены (на момент ошибки) ---")
            for token in tokens:
                print(token)
        if rpn:
            print("\\n--- ОПЗ (на момент ошибки) ---")
            for i, item in enumerate(rpn):
                print(f"{i}: {item}")
        sys.exit(1)

if __name__ == "__main__":
    main()
