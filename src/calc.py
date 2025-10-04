"""
автор: Смирнов Никита
группа: М8О-101-БВ-25
вариант: M1
"""

from typing import cast

from src.constants import ReConst


class CalcError(Exception):
    """Понятные ошибки калькулятора."""

    pass


class Calc:
    """
    Класс, объединяющий методы, необходымые для калькулятора.
    Для использования методов: Calc.МЕТОД_ИЗ_ЭТОГО_КЛАССА(НЕОБХОДИМЫЕ_АРГУМЕНТЫ).
    Создавать экземляр этого класса не нужно.
    """

    Token = tuple[str, float | None]

    def __new__(cls, in_: str) -> float:
        """
        Переопределенный метод __new__.
        Служит как синоним Calc.eval.
        """
        return cls.eval(in_)

    @staticmethod
    def parse(in_: str) -> list[str]:
        """
        Получет строку, и разбивает её на отдельные числа, опрераторы и скобки, используя регульрыне выражения.
        При невозможности разделить строку - вызывает исключение
        """
        try:
            in_ = in_.strip()
            return [m.group(1) for m in ReConst.TOKEN_RE.finditer(in_)]
        except:  # noqa: E722
            raise CalcError(
                "Вход не соответсвует требуемому шаблону: еще раз проверь праивльность выражения"
            )

    @staticmethod
    def tokenize(expr: list[str]) -> list[Token]:
        """
        Разбить строку на токены: числа, операторы и скобки.
        Для числа кладём ("NUM", float_value).
        Для оператора и скобок кладём (символ, None).
        В конец добавляем ("EOF", None)
        """
        tokens = []

        for e in expr:
            if e in ReConst.ARITHM or e in ReConst.BRACKET:
                tokens.append((e, None))
            else:
                tokens.append(("NUM", float(e)))

        return tokens + [("EOF", None)]

    @staticmethod
    def check_brackets(tokens: list[Token]) -> bool:
        """
        Проверяет в списке токенов правильность расположения скобок (без учета арифметических операций).
        """
        stack = []

        for token in tokens:
            if token[0] == "(":
                stack.append(token)
            elif token[0] == ")":
                if not stack:
                    return False
                stack.pop()

        return not stack

    @staticmethod
    def validate_expr(in_: str) -> bool:
        """
        Проверяет, что в выражении нет недопустимых символов
        """
        return bool(ReConst.EXPR.match(in_))

    @staticmethod
    def parse_add(tokens: list[Token], i: int) -> tuple[float, int]:
        """
        add := mull (('+'|'-') mull)*
        Складываем/вычитаем mul по мере чтения.
        """
        v, i = Calc.parse_mull(tokens, i)

        while tokens[i][0] in ("+", "-"):
            op = tokens[i][0]
            i += 1
            rhs, i = Calc.parse_mull(tokens, i)
            v = v + rhs if op == "+" else v - rhs

        return v, i

    @staticmethod
    def parse_mull(tokens: list[Token], i: int) -> tuple[float, int]:
        """
        mull := pow (('*'|'/'|'//'|'%') pow)*
        Выполняем умножения/деления по мере чтения (лево-ассоциативно).
        """
        v, i = Calc.parse_pow(tokens, i)

        while tokens[i][0] in ("*", "/", "//", "%"):
            op = tokens[i][0]
            i += 1
            rhs, i = Calc.parse_pow(tokens, i)

            match op:
                case "/":
                    if rhs == 0:
                        raise CalcError("Деление на ноль")
                    v = v / rhs
                case "//":
                    if rhs == 0:
                        raise CalcError("Деление на ноль")
                    if v.is_integer() and rhs.is_integer():
                        v = v // rhs
                    else:
                        raise CalcError(
                            "Целочисленное деление допустимо с целыми числами: "
                        )
                case "%":
                    if v.is_integer() and rhs.is_integer():
                        v = v % rhs
                    else:
                        raise CalcError(
                            "Взятие остатка от деления допустимо с целыми числами"
                        )
                case "*":
                    v = v * rhs

        return v, i

    @staticmethod
    def parse_pow(tokens: list[Token], i: int) -> tuple[float, int]:
        """
        pow := primary ('**' pow)?
        Выполняем возведение в степень по мере чтения (право-ассоциативно).
        """
        v, i = Calc.parse_primary(tokens, i)

        if tokens[i][0] == "**":
            i += 1
            rhs, i = Calc.parse_pow(tokens, i)
            if v == 0 and rhs == 0:
                raise CalcError("Неопределенность 0**0")
            v = v**rhs

        return v, i

    @staticmethod
    def parse_primary(tokens: list[Token], i: int) -> tuple[float, int]:
        """
        primary := NUM | add
        Возвращаем число, если токен NUM или вызываем add для скобок.
        """
        if tokens[i][0] == "(":
            i += 1
            v, i = Calc.parse_add(tokens, i)
            if tokens[i][0] != ")":
                raise CalcError("Несоответствующая закрывающая скобка")
            i += 1
            return v, i

        if tokens[i][0] == "NUM":
            v = cast(float, tokens[i][1])
            i += 1
            return (v, i)

        raise CalcError("Некорректный токен")

    @staticmethod
    def eval(in_: str) -> float:
        """
        Основной интерфейс калькулятора.
        Получает строковое выражение.
        Проводит первичные проверки у разбиение на токены.
        Вычисляет и возвращает результат в формате действительныго числа.
        """
        if not Calc.validate_expr(in_):
            raise CalcError("В выражении присутвуют недопустимые символы")

        expr = Calc.parse(in_)
        tokens = Calc.tokenize(expr)

        if not Calc.check_brackets(tokens):
            raise CalcError("Неправильно расставлыны скобки")

        v, i = Calc.parse_add(tokens, 0)

        return v
