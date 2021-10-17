import pytest

from pygdk.mill import Mill
from pygdk.machine import Machine

def test_mill_successful_init():
    mill = Mill('onefinity.json')
    assert isinstance(mill, Mill)
    assert isinstance(mill, Machine)

def test_mill_missing_conf():
    with pytest.raises(FileNotFoundError):
        mill = Mill('non-existent.json')

def test_mill_blank_conf():
    with pytest.raises(ValueError):
        mill = Mill('')

def test_mill_null_conf():
    with pytest.raises(ValueError):
        mill = Mill(None)

def test_mill_conf_not_provided():
    with pytest.raises(TypeError):
        mill = Mill()

def test_mill_conf_with_bad_tt():
    with pytest.raises(FileNotFoundError):
        mill = Mill('tests/bad_tt.json')

def test_mill_conf_with_no_tt():
    with pytest.raises(KeyError):
        mill = Mill('tests/no_tt.json')
