import pytest

from pygdk.lathe import Lathe
from pygdk.machine import Machine

def test_lathe_successful_init():
    lathe = Lathe('orac.json')
    assert isinstance(lathe, Lathe)
    assert isinstance(lathe, Machine)

def test_lathe_missing_conf():
    with pytest.raises(FileNotFoundError):
        lathe = Lathe('non-existent.json')

def test_lathe_blank_conf():
    with pytest.raises(ValueError):
        lathe = Lathe('')

def test_lathe_null_conf():
    with pytest.raises(ValueError):
        lathe = Lathe(None)

def test_lathe_conf_not_provided():
    with pytest.raises(TypeError):
        lathe = Lathe()

def test_lathe_conf_with_bad_tt():
    with pytest.raises(FileNotFoundError):
        lathe = Lathe('tests/bad_tt.json')

def test_lathe_conf_with_no_tt():
    with pytest.raises(KeyError):
        lathe = Lathe('tests/no_tt.json')
