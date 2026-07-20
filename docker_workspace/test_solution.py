import pytest
from solution import solution

# Test with two positive integers
def test_positive_integers():
    assert solution(1, 2) == 3

# Test with two negative integers
def test_negative_integers():
    assert solution(-1, -2) == -3

# Test with a positive and a negative integer
def test_positive_and_negative():
    assert solution(5, -3) == 2

# Test with zero and a positive number
def test_zero_and_positive():
    assert solution(0, 5) == 5

# Test with zero and a negative number
def test_zero_and_negative():
    assert solution(0, -5) == -5

# Test with two floating point numbers
def test_floats():
    assert solution(1.5, 2.5) == 4.0

# Test with one float and one integer
def test_float_and_integer():
    assert solution(2.5, 2) == 4.5

# Test with large integers
def test_large_integers():
    assert solution(1000000000, 2000000000) == 3000000000

# Test with very small (close to zero) floats
def test_small_floats():
    assert solution(1e-10, 1e-10) == 2e-10
