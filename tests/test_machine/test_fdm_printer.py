import pytest

from pygdk.fdm_printer import FDMPrinter
from pygdk.machine import Machine

def test_fdm_printer_successful_init():
    fdm_printer = FDMPrinter('kossel.json')
    assert isinstance(fdm_printer, FDMPrinter)
    assert isinstance(fdm_printer, Machine)

def test_fdm_printer_missing_conf():
    with pytest.raises(FileNotFoundError):
        fdm_printer = FDMPrinter('non-existent.json')

def test_fdm_printer_blank_conf():
    with pytest.raises(FileNotFoundError):
        fdm_printer = FDMPrinter('')

def test_fdm_printer_null_conf():
    with pytest.raises(TypeError):
        fdm_printer = FDMPrinter(None)

def test_fdm_printer_conf_not_provided():
    with pytest.raises(TypeError):
        fdm_printer = FDMPrinter()

def test_fdm_printer_conf_with_bad_filament_table():
    with pytest.raises(FileNotFoundError):
        fdm_printer = FDMPrinter('tests/test_machine/bad_filament.json')

def test_fdm_printer_conf_with_no_filament_table():
    with pytest.raises(KeyError):
        fdm_printer = FDMPrinter('onefinity.json')
