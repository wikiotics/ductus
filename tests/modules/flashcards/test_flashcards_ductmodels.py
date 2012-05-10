import pytest

from ductus.resource import ductmodels
from ductus.modules.flashcards.ductmodels import _divider_validator

def test_divider_validator():
    _divider_validator(None)
    _divider_validator('')
    _divider_validator('4')
    _divider_validator('4,5')
    with pytest.raises(ductmodels.ValidationError):
        _divider_validator('4,,5')
    with pytest.raises(ductmodels.ValidationError):
        _divider_validator('5,3')
    with pytest.raises(ductmodels.ValidationError):
        _divider_validator('4,5,5')
    with pytest.raises(ductmodels.ValidationError):
        _divider_validator('4, 5,5')
    with pytest.raises(ductmodels.ValidationError):
        _divider_validator('4,x')
