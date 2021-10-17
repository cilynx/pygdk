import pytest

from pygdk.plotter import Plotter
from pygdk.machine import Machine

def test_plotter_successful_init():
    plotter = Plotter('onefinity.json')
    assert isinstance(plotter, Plotter)
    assert isinstance(plotter, Machine)

def test_plotter_missing_conf():
    with pytest.raises(FileNotFoundError):
        plotter = Plotter('non-existent.json')

def test_plotter_blank_conf():
    with pytest.raises(FileNotFoundError):
        plotter = Plotter('')

def test_plotter_null_conf():
    with pytest.raises(TypeError):
        plotter = Plotter(None)

def test_plotter_conf_not_provided():
    with pytest.raises(TypeError):
        plotter = Plotter()

def test_plotter_conf_with_no_plotter():
    with pytest.raises(KeyError):
        plotter = Plotter('tests/test_machine/bad_tt.json')
