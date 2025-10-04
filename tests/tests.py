import unittest

from src.calc import Calc, CalcError


class TestParse(unittest.TestCase):
    def test_basic_numbers(self):
        self.assertEqual(Calc.parse("42"), ["42"])
        self.assertEqual(Calc.parse("-3.5"), ["-3.5"])
        self.assertEqual(Calc.parse("+7"), ["+7"])

    def test_with_spaces_and_ops(self):
        self.assertEqual(Calc.parse("  -5.1 + 2*3 "), ["-5.1", "+", "2", "*", "3"])
        self.assertEqual(Calc.parse("(2+3)*4"), ["(", "2", "+", "3", ")", "*", "4"])

    def test_power_and_floor_div(self):
        self.assertEqual(Calc.parse("2**3"), ["2", "**", "3"])
        self.assertEqual(Calc.parse("7 // 3 + 1"), ["7", "//", "3", "+", "1"])


class TestTokenize(unittest.TestCase):
    def test_simple(self):
        tokens = Calc.tokenize(["2", "+", "3"])
        self.assertEqual(
            tokens, [("NUM", 2.0), ("+", None), ("NUM", 3.0), ("EOF", None)]
        )

    def test_with_unary(self):
        tokens = Calc.tokenize(["-3", "*", "+2"])
        self.assertEqual(
            tokens, [("NUM", -3.0), ("*", None), ("NUM", 2.0), ("EOF", None)]
        )

    def test_brackets(self):
        tokens = Calc.tokenize(["(", "-2", "+", "3", ")"])
        self.assertEqual(
            tokens,
            [
                ("(", None),
                ("NUM", -2.0),
                ("+", None),
                ("NUM", 3.0),
                (")", None),
                ("EOF", None),
            ],
        )


class TestBrackets(unittest.TestCase):
    def test_valid_brackets(self):
        tokens = Calc.tokenize(Calc.parse("(1+(2*3))"))
        self.assertTrue(Calc.check_brackets(tokens))

    def test_invalid_brackets(self):
        tokens = Calc.tokenize(["(", "1", "+", "2"])
        self.assertFalse(Calc.check_brackets(tokens))


class TestValidate(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(Calc.validate_expr(" 7 // 3 + 2 "))
        self.assertTrue(Calc.validate_expr(" (2+3)*4 "))

    def test_invalid(self):
        self.assertFalse(Calc.validate_expr(" 7 // 3 + a "))
        self.assertFalse(Calc.validate_expr(" 2 ** 3 # 5"))


class TestEval(unittest.TestCase):
    def test_basic_ops(self):
        self.assertEqual(Calc.eval("2+3"), 5)
        self.assertEqual(Calc.eval("2-5"), -3)
        self.assertEqual(Calc.eval("2*3+4"), 10)
        self.assertEqual(Calc.eval("(2+3)*4"), 20)

    def test_division(self):
        self.assertEqual(Calc.eval("10/2"), 5)
        self.assertEqual(Calc.eval("7//3"), 2)
        self.assertEqual(Calc.eval("7%3"), 1)

    def test_power_right_assoc(self):
        self.assertEqual(Calc.eval("2**3**2"), 512)  # 2 ** (3 ** 2)

    def test_unary(self):
        self.assertEqual(Calc.eval("-3+5"), 2)
        self.assertEqual(Calc.eval("+3+5"), 8)

    def test_errors(self):
        with self.assertRaises(CalcError):
            Calc.eval("2/0")
        with self.assertRaises(CalcError):
            Calc.eval("2//0")
        with self.assertRaises(CalcError):
            Calc.eval("2//2.5")
        with self.assertRaises(CalcError):
            Calc.eval("5.1%2")
        with self.assertRaises(CalcError):
            Calc.eval("0**0")
        with self.assertRaises(CalcError):
            Calc.eval("(2+3")
        with self.assertRaises(CalcError):
            Calc.eval("2+2 junk")


if __name__ == "__main__":
    unittest.main()
