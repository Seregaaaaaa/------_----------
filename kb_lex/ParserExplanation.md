# Синтаксический анализатор и генератор ОПС

## Общее описание

Данная реализация представляет собой комплексную систему анализа и обработки исходного кода на языке KB-Lex. Система включает синтаксический анализатор, использующий магазинный автомат по принципу LL(1)-парсера, табличный генератор обратной польской записи (ОПС) и таблицу символов для управления контекстной информацией.

## Компоненты

### 1. Синтаксический анализатор (Parser)

Синтаксический анализатор - это ключевой компонент системы, который преобразует поток токенов в синтаксически корректные конструкции языка и координирует работу всех остальных компонентов.

#### Основные характеристики:
- **Реализация**: Файл `parser.py`
- **Тип анализатора**: Магазинный (стековый) автомат LL(1)
- **Принцип работы**: Нисходящий разбор с предсказанием по одному символу
- **Основа**: КС-грамматика в форме Грейбаха

#### Ключевые структуры данных парсера:
- **Стек (self.stack)**: Основная структура для хранения символов разбора (терминалов и нетерминалов)
- **Таблица синтаксического анализа**: Словарь словарей, определяющий правила замены нетерминалов в зависимости от входных токенов
- **Стек типов данных (self.data_types_stack)**: Хранит информацию о типах данных для объявлений переменных
- **Стек меток (self.label_stack)**: Управляет адресами переходов для условных конструкций и циклов
- **Контекстная информация (self.context)**: Словарь, хранящий текущее состояние разбора (внутри объявления, внутри цикла и т.д.)

#### Основные методы:
- **parse()**: Основной метод анализа, управляющий процессом разбора
- **build_parse_table()**: Создает таблицу синтаксического анализа для LL(1) парсера
- **is_terminal()**, **is_nonterminal()**: Определяют тип символа (терминал/нетерминал)
- **execute_semantic_action()**: Выполняет семантические программы при обработке различных конструкций
- **handle_variable_declaration()**, **handle_array_declaration()**: Специализированные методы для обработки объявления переменных и массивов

### 2. Генератор ОПС (RPNGenerator)

Генератор обратной польской записи преобразует структуры языка в последовательность команд, которая может быть выполнена стековой машиной.

#### Основные характеристики:
- **Реализация**: Файл `rpn_generator.py`
- **Формат вывода**: Линейная последовательность команд и операндов
- **Оптимизация**: Минимальный размер генерируемого кода

#### Поддерживаемые типы команд:
- **Операнды**: Идентификаторы переменных, числовые константы
- **Арифметические операторы**: Сложение (PLUS), вычитание (MINUS), умножение (MULTIPLY), деление (DIVIDE)
- **Логические операторы**: Сравнение (LT, GT), проверка равенства/неравенства (EQUALS, NEQ), логические связки (AND, OR)
- **Унарные операторы**: Отрицание (UNARY_MINUS)
- **Операторы перехода**: Безусловный переход (J), условный переход (JF)
- **Операции ввода/вывода**: Вывод значений (W), ввод значений (R)
- **Операции с массивами**: Индексация (I), инициализация списком (LIST, GEN)

#### Основные методы:
- **add_identifier()**: Добавление идентификатора в ОПС
- **add_constant()**: Добавление константы в ОПС
- **add_operator()**: Добавление оператора с преобразованием в формат ОПС
- **add_jump()**, **add_conditional_jump()**: Добавление безусловных и условных переходов
- **replace_label_placeholder()**: Замена заполнителей адресов на реальные адреса
- **get_rpn()**: Получение готовой обратной польской записи

### 3. Таблица символов (SymbolTable)

Таблица символов - это структура данных, которая отслеживает все переменные и их свойства в процессе анализа программы.

#### Основные характеристики:
- **Реализация**: Файл `symbol_table.py`
- **Основа**: Набор специализированных словарей для разных типов переменных
- **Назначение**: Контроль типов, проверка повторных объявлений, проверка существования переменных

#### Хранимые типы данных:
- **Целочисленные переменные (int_vars)**: Словарь для обычных целых переменных
- **Вещественные переменные (float_vars)**: Словарь для переменных с плавающей точкой
- **Целочисленные массивы (int_arrays)**: Словарь для массивов целых чисел
- **Вещественные массивы (float_arrays)**: Словарь для массивов с плавающей точкой

#### Основные методы:
- **add_variable()**: Добавление новой переменной заданного типа с проверкой на повторные объявления
- **exists()**: Проверка существования переменной в любом из словарей
- **get_variable_type()**: Определение типа переменной по имени
- **is_array()**: Проверка, является ли переменная массивом

## Алгоритм работы

### Общий алгоритм

1. **Инициализация**:
   - Лексический анализатор преобразует исходный текст программы в последовательность токенов
   - Синтаксический анализатор создаёт пустой стек и помещает в него маркер конца файла (EOF) и начальный нетерминал `<Программа>`
   - Инициализируется генератор ОПС, таблица символов, стек типов и стек меток

2. **Основной цикл разбора**:
   - Пока стек не пуст:
     * Анализатор извлекает верхний символ из стека
     * Проверяет наличие и выполняет соответствующие семантические действия
     * Обрабатывает символ в зависимости от его типа (терминал/нетерминал/специальный символ)

3. **Обработка терминалов**:
   - Если верхний символ стека - терминал:
     * Если совпадает с текущим входным токеном, токен потребляется и парсер переходит к следующему
     * Если идентификатор - добавляется в ОПС
     * Если константа - добавляется в ОПС с её значением
     * Если ключевое слово типа (`int`, `float`) - записывается в стек типов
     * Если не совпадает с входным токеном - генерируется синтаксическая ошибка

4. **Обработка нетерминалов**:
   - Если верхний символ стека - нетерминал:
     * Парсер ищет правило в таблице синтаксического анализа по паре (нетерминал, текущий токен)
     * Если правило найдено, нетерминал заменяется на правую часть правила (символы добавляются в обратном порядке)
     * Если правило не найдено, проверяется наличие пустого правила (lambda)
     * Если ничего не найдено - генерируется синтаксическая ошибка

5. **Обработка операторов и специальных символов**:
   - Если верхний символ стека - оператор или специальный символ:
     * Генератор ОПС добавляет соответствующую команду
     * Например, для `+` добавляется `PLUS`, для `=` добавляется `ASSIGN`, и т.д.

6. **Завершение**:
   - Если стек опустошен или на верхушке стека и во входном потоке находятся EOF - разбор успешно завершен
   - Возвращается список сгенерированных команд ОПС

### Детали работы с контекстом

1. **Объявление переменных**:
   - При обнаружении типа данных (`int`, `float`) тип помещается в стек типов
   - При обнаружении `[` к типу в стеке добавляется признак массива (`intarr`, `floatarr`)
   - При обработке идентификатора выполняется проверка на повторное объявление и добавление в таблицу символов

2. **Присваивание**:
   - Значение выражения вычисляется и помещается на стек
   - Идентификатор помещается в ОПС
   - Генерируется оператор присваивания (ASSIGN)

3. **Условные операторы**:
   - Разбор выражения условия с генерацией соответствующей ОПС
   - При завершении условия генерируется условный переход (JF) с временной меткой
   - После блока `then` генерируется безусловный переход (J) для пропуска блока `else`
   - Метки заполняются правильными адресами после разбора всех блоков

4. **Циклы**:
   - Адрес начала цикла сохраняется в стек меток
   - Разбор условия с генерацией ОПС
   - Условный переход (JF) с временной меткой для выхода из цикла
   - После тела цикла генерируется безусловный переход (J) на начало цикла
   - Метка выхода заполняется правильным адресом

## Основные структуры данных

### 1. Магазин (стек) синтаксического анализатора

Стек является центральной структурой данных LL(1)-парсера и содержит символы, которые еще предстоит обработать:

- **Содержимое**: Терминалы, нетерминалы и специальные символы
- **Порядок обработки**: Сверху вниз (LIFO - последний пришёл, первый ушёл)
- **Операции**:
  * `append()` - добавление элемента на верхушку стека
  * `pop()` - извлечение и удаление верхнего элемента стека
  * `[-1]` - чтение верхнего элемента без удаления

### 2. Таблица синтаксического анализа

Двумерная таблица, реализованная как словарь словарей:

- **Ключи первого уровня**: Нетерминальные символы грамматики
- **Ключи второго уровня**: Терминальные символы (токены)
- **Значения**: Список символов правой части правила
- **Размер**: Число нетерминалов × число терминалов
- **Особенности**: Включает правила для обработки всех допустимых языковых конструкций
- **Применение**: Определяет, какую последовательность символов нужно положить в стек при обработке нетерминала

### 3. Обратная польская запись (ОПС)

Линейный список с командами и операндами в последовательности, готовой к выполнению:

- **Структура**: Одномерный список строк
- **Принцип формирования**: Операнды следуют в порядке появления, операторы - после своих операндов
- **Индексация**: Каждая команда или операнд имеет уникальный индекс в списке
- **Преимущества**: Не требует скобок, удобна для интерпретации, поддерживает эффективное вычисление выражений

### 4. Стек меток для управления потоком выполнения

Специализированный стек для хранения адресов в ОПС:

- **Назначение**: Управление условными и безусловными переходами
- **Операции**:
  * Сохранение текущего индекса ОПС при начале управляющих конструкций
  * Извлечение адресов для заполнения команд перехода
- **Применение**: Реализация структурных конструкций (if-else, while) с использованием переходов

### 5. Стек типов данных

Стек для отслеживания типов объявляемых переменных:

- **Содержимое**: Строки с именами типов ("int", "float", "intarr", "floatarr")
- **Применение**: При объявлении переменных для определения их типа и проверки совместимости

### 6. Контекстная информация

Словарь с флагами для управления синтаксическим анализом:

- **Ключи**: Строковые идентификаторы контекстных состояний
- **Значения**: Булевы флаги и дополнительная информация
- **Назначение**: Отслеживание текущего контекста анализа (объявление переменных, присваивание, условные выражения и т.д.)

## Семантические программы

Семантические программы - это действия, выполняемые при обнаружении определённых синтаксических конструкций. Они генерируют правильный код ОПС и поддерживают контекстную информацию.

### Программа 1: Обработка типов данных
- **Событие**: Распознавание ключевого слова `int` или `float`
- **Действие**: Запись соответствующего типа в стек типов данных
- **Применение**: Начало объявления переменных соответствующего типа

### Программа 2: Обработка объявления массива
- **Событие**: Распознавание `[` после типа данных
- **Действие**: Извлечение текущего типа из стека, добавление признака массива, запись обновленного типа обратно в стек
- **Результат**: Тип "int" преобразуется в "intarr", "float" в "floatarr"

### Программа 3: Объявление переменной
- **Событие**: Распознавание идентификатора в контексте объявления переменной
- **Действия**:
  * Проверка на повторное объявление
  * Добавление переменной в соответствующую часть таблицы символов с типом из стека типов
  * Добавление идентификатора в ОПС

### Программа 4: Инициализация массива
- **Событие**: Распознавание `=` после объявления массива
- **Действия**:
  * Добавление операции `LIST` в ОПС для начала инициализации
  * После обработки списка добавление операции `$GEN` для завершения инициализации

### Программа 5: Индексация массива
- **Событие**: Распознавание `[` после идентификатора переменной
- **Действия**:
  * Проверка, является ли переменная массивом
  * После обработки индекса добавление операции `$i` в ОПС

### Программы 6-8: Обработка циклов while
- **Программа 6 (Начало while)**: Сохранение текущего индекса в стек меток (адрес начала цикла)
- **Программа 7 (После условия while)**: 
  * Сохранение текущего индекса (для последующего заполнения адреса выхода)
  * Добавление условного перехода `$JF` с временной меткой
- **Программа 8 (Конец блока while)**:
  * Извлечение адресов из стека меток
  * Заполнение метки для условного перехода
  * Добавление безусловного перехода `$J` на начало цикла

### Программы 9-11: Обработка условного оператора if-else
- **Программа 9 (После условия if)**: 
  * Сохранение текущего индекса в стек меток
  * Добавление условного перехода `$JF` с временной меткой
- **Программа 10 (Конец блока if без else)**:
  * Извлечение адреса команды условного перехода
  * Заполнение метки адресом текущей позиции
- **Программа 11 (Начало блока else)**:
  * Извлечение адреса команды условного перехода
  * Добавление безусловного перехода `$J` для пропуска блока else
  * Заполнение метки условного перехода адресом текущей позиции

### Дополнительные программы для специальных операций
- **Ввод/вывод**: Добавление операторов `$r` (ввод) и `$w` (вывод) в ОПС
- **Операции с массивами**: Обработка индексации (`$i`) и инициализации массивов (`LIST`, `$GEN`)
- **Арифметические и логические операторы**: Добавление соответствующих команд в ОПС

## Формат ОПС и его интерпретация

Обратная польская запись (ОПС) - это последовательность операндов и операторов, представленная в постфиксной нотации, которая не требует скобок и имеет однозначную интерпретацию.

### Основные элементы ОПС:

1. **Идентификаторы переменных**
   - **Формат**: Строка с именем переменной (например, `"a"`, `"counter"`)
   - **Интерпретация**: Значение переменной помещается на стек вычислений

2. **Константы**
   - **Формат**: Числовые значения (целые или с плавающей точкой)
   - **Примеры**: `213`, `3.1415`
   - **Интерпретация**: Значение константы помещается на стек вычислений

3. **Арифметические операторы**
   - **PLUS**: Сложение двух верхних значений стека
   - **MINUS**: Вычитание верхнего значения из предыдущего
   - **MULTIPLY**: Умножение двух верхних значений стека
   - **DIVIDE**: Деление предыдущего значения на верхнее

4. **Операторы сравнения и логические операторы**
   - **LT**: Меньше (`<`), результат - булево значение
   - **GT**: Больше (`>`), результат - булево значение
   - **NEQ**: Не равно (`!`), результат - булево значение
   - **EQUALS**: Равно (`?`), результат - булево значение
   - **AND**: Логическое И (`&`), объединяет два булевых значения
   - **OR**: Логическое ИЛИ (`|`), объединяет два булевых значения
   - **UNARY_MINUS**: Унарный минус (`~`), меняет знак верхнего значения

5. **Операции ввода/вывода**
   - **$w**: Вывод верхнего значения стека
   - **$r**: Ввод значения и помещение его на стек

6. **Операции с массивами**
   - **$i**: Индексация массива (извлекает элемент массива по индексу)
   - **LIST**: Начало инициализации массива
   - **$GEN**: Завершение инициализации массива

7. **Операторы перехода**
   - **$J адрес**: Безусловный переход на указанный адрес в ОПС
   - **$JF адрес**: Условный переход (если верхнее значение стека - false)

### Пример работы с ОПС:

Для выражения `a = b * (c + d)`:

```
b c d PLUS MULTIPLY a ASSIGN
```

Для условной конструкции `if (a > b) { output a; }`:

```
a b GT $JF 5 a $w 5: (следующая команда)
```

Преимущества формата ОПС:
- Не требует дополнительного разбора при интерпретации
- Позволяет эффективно вычислять выражения с использованием стека
- Упрощает генерацию машинного кода для большинства архитектур процессоров

## Примеры преобразования программ в ОПС

### Пример 1: Объявление и инициализация переменной
**Исходный код:**
```
int a = 213;
```

**Токены:**
```
INT, IDENTIFIER(a), ASSIGN, INTEGER_CONST(213), SEMICOLON
```

**ОПС:**
```
a 213 ASSIGN
```

### Пример 2: Объявление и инициализация массива
**Исходный код:**
```
int[] b = {1, 2};
```

**Токены:**
```
INT, LSQUARE, RSQUARE, IDENTIFIER(b), ASSIGN, LCURLY, INTEGER_CONST(1), COMMA, INTEGER_CONST(2), RCURLY, SEMICOLON
```

**ОПС:**
```
b LIST 1 2 $GEN
```

### Пример 3: Условный оператор
**Исходный код:**
```
if (a ? b[1]) {
    output a;
} else {
    output b[0];
}
```

**ОПС:**
```
a b 1 $i EQUALS $JF 6 a $w $J 9 b 0 $i $w
```

### Пример 4: Цикл while
**Исходный код:**
```
int i = 0;
while (i < 10) {
    i = i + 1;
    output i;
}
```

**ОПС:**
```
i 0 ASSIGN
6: i 10 LT $JF 14 i i 1 PLUS ASSIGN i $w $J 6 14:
```

## Обработка ошибок

Синтаксический анализатор включает механизмы обнаружения и обработки различных типов ошибок:

### 1. Синтаксические ошибки
- **Пример**: Отсутствие обязательного символа (например, `;` после оператора)
- **Действие**: Генерация исключения `SyntaxError` с указанием строки и позиции

### 2. Семантические ошибки
- **Пример**: Повторное объявление переменной, использование необъявленной переменной
- **Действие**: Генерация исключения с соответствующим сообщением

### 3. Ошибки типов
- **Пример**: Попытка использовать обычную переменную как массив
- **Действие**: Генерация исключения с указанием несовместимых типов

## Преимущества и ограничения реализации

### Преимущества:
1. **Модульность**: Чёткое разделение компонентов (лексер, парсер, генератор ОПС, таблица символов)
2. **Расширяемость**: Возможность добавления новых языковых конструкций и типов данных
3. **Диагностика ошибок**: Подробные сообщения об ошибках с указанием строки и позиции
4. **Эффективность**: Минимальное использование памяти и высокая скорость анализа

### Ограничения:
1. **Ограниченный набор типов**: Поддерживаются только int, float и их массивы
2. **Отсутствие функций**: Реализация не включает определение и вызов функций
3. **Оптимизация**: Генерируемый код не проходит дополнительную оптимизацию

## Заключение

Разработанный синтаксический анализатор и генератор ОПС представляет собой полноценную основу компилятора для языка KB-Lex. Система поддерживает все основные конструкции языка, включая переменные, массивы, условные операторы, циклы, арифметические и логические выражения, операции ввода/вывода.

Архитектура системы обеспечивает чёткое разделение ответственности между компонентами, что упрощает её дальнейшее развитие и модификацию. Генерируемая обратная польская запись является промежуточным представлением программы, которое может быть легко интерпретировано или преобразовано в машинный код целевой платформы.
