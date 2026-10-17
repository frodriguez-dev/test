from calculator import add, subtract


def test_add():
    assert add(2, 3) == 5


def test_subtract_two_positive_numbers():
    assert subtract(5, 3) == 2


def test_subtract_negative_result():
    assert subtract(3, 5) == -2


def test_subtract_negative_numbers():
    assert subtract(-5, -3) == -2


def test_subtract_zero_result():
    assert subtract(4, 4) == 0
