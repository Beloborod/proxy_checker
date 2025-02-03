import pytest
from src.wire_web_driver import Driver, DriverWrapper


@pytest.mark.dependency(scope='session')
def test_driver():
    assert type(Driver()) is Driver


@pytest.mark.dependency(scope='session')
def test_driver_wrapper():
    assert type(DriverWrapper()) is DriverWrapper
