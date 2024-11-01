import streamlit as st
from sympy import sympify, zoo, nan
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
import re


# Функция для обработки ввода чисел
def parse_input(value):
    if value:
        # Заменяем запятые на точки и удаляем лишние пробелы
        value = value.replace(',', '.').strip()

        # Обновлённое регулярное выражение
        pattern = r'^[+-]?(\d{1,3}( \d{3})*(\.\d+)?|\d+(\.\d+)?)$'

        if re.match(pattern, value):
            try:
                decimal_value = Decimal(value.replace(' ', '')).quantize(Decimal('0.0000000000'),
                                                                         rounding=ROUND_HALF_UP)
                return decimal_value
            except InvalidOperation:
                return None
    return None


# Форматирование числа
def format_number(number):
    # Округление до 6 знаков после запятой
    rounded = number.quantize(Decimal('0.000000'), rounding=ROUND_HALF_UP)

    # Нормализация числа, чтобы удалить незначащие нули
    normalized = rounded.normalize()

    # Форматирование числа с пробелами вместо запятых
    str_number = f"{normalized:,.6f}".replace(',', ' ')

    # Убираем незначащие нули в конце
    str_number = str_number.rstrip('0').rstrip('.') if '.' in str_number else str_number

    # Убираем .000000, если число целое
    if normalized == normalized.to_integral_value():
        str_number = str(normalized.to_integral_value()).replace(',', ' ')

    return str_number


# Округление итогового результата
def round_result(value, method):
    # Округление в зависимости от метода
    if method == "Математическое":
        rounded_value = value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    elif method == "Бухгалтерское":
        rounded_value = value.quantize(Decimal('1'), rounding=ROUND_HALF_EVEN)
    elif method == "Усечение":
        rounded_value = value.quantize(Decimal('1'), rounding=ROUND_DOWN)
    else:
        raise ValueError("Неизвестный метод округления")

    # Форматирование с пробелами для тысяч
    str_result = f"{rounded_value:,.0f}".replace(',', ' ')

    return str_result


# Заголовок приложения
st.title("Калькулятор")

# Информация о студенте
st.write("ФИО: Киселев Никита Леонидович")
st.write("Курс: 3")
st.write("Группа: 11")
st.write("Год: 2024")

# Ввод чисел
num1 = st.text_input("Введите первое число:", "0")
operation1 = st.selectbox("Операция 1-2:", ["+", "-", "*", "/"], index=0)
num2 = st.text_input("Введите второе число:", "0")
operation2 = st.selectbox("Операция 2-3 (приоритетная):", ["+", "-", "*", "/"], index=0)
num3 = st.text_input("Введите третье число:", "0")
operation3 = st.selectbox("Операция 3-4:", ["+", "-", "*", "/"], index=0)
num4 = st.text_input("Введите четвертое число:", "0")

if 'final_result' not in st.session_state:
    st.session_state.final_result = None
if 'formatted_result' not in st.session_state:
    st.session_state.formatted_result = None
if 'rounded_result' not in st.session_state:
    st.session_state.rounded_result = None

if st.button("Вычислить"):
    try:
        number1 = parse_input(num1)
        print(number1)
        number2 = parse_input(num2)
        number3 = parse_input(num3)
        number4 = parse_input(num4)

        if number1 is None or number2 is None or number3 is None or number4 is None:
            st.error("Пожалуйста, введите корректные числа.")
            st.session_state.final_result = None
            st.session_state.formatted_result = None
            st.stop()

        expression = f"{number1} {operation1} ({number2} {operation2} {number3}) {operation3} {number4}"

        try:
            result = sympify(expression)
            print("a")
            print(result)
            # Проверяем, является ли результат неопределенным
            if result in [zoo, nan]:
                st.error("Ошибка: Деление на 0 невозможно.")
                st.session_state.final_result = None  # Сбрасываем результат
                st.session_state.formatted_result = None
            else:
                result_evaluated = result.evalf(20)
                print(result_evaluated)
                # Преобразование в Decimal
                final_result = Decimal(str(result_evaluated)).quantize(Decimal('0.0000000000'), rounding=ROUND_HALF_UP)
                str_final_result = format(final_result, 'f')
                print(str_final_result)
                # Проверка диапазона итогового результата

                if final_result < Decimal('-10000000000000.0000000000') or final_result > Decimal(
                        '10000000000000.0000000000'):
                    st.error("Итоговый результат выходит за пределы диапазона.")
                    st.session_state.final_result = None
                    st.session_state.formatted_result = None
                else:
                    # Сохраняем результаты для дальнейшего использования
                    st.session_state.final_result = final_result
                    st.session_state.formatted_result = format_number(final_result)
                    st.session_state.rounded_result = None

        except Exception as e:
            st.error(f"Ошибка при вычислении выражения: {str(e)}")
            st.session_state.final_result = None
            st.session_state.formatted_result = None

    except Exception as e:
        st.error(f"Ошибка при вычислении: {str(e)}")
        st.session_state.final_result = None
        st.session_state.formatted_result = None

# Если результат уже вычислен, показываем выбор округления
if st.session_state.final_result is not None:
    st.success(f"Результат: {st.session_state.formatted_result}")
    rounding_method = st.selectbox("Выберите метод округления результата:",
                                   ["Математическое", "Бухгалтерское", "Усечение"])
    if st.button("Округлить"):
        st.session_state.rounded_result = round_result(st.session_state.final_result, rounding_method)
        st.success(f"Округленный результат: {st.session_state.rounded_result}")

st.write("Вы можете использовать Ctrl+C и Ctrl+V для вставки и копирования чисел.")
