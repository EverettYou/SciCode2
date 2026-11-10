"""Portable exact rational witnesses, compatible with extension hex encoding."""
from fractions import Fraction as F
def encode(value):
 value=F(value);return {'numerator_hex':hex(value.numerator),'denominator_hex':hex(value.denominator)}
def decode(value):
 if isinstance(value,dict):return F(int(value['numerator_hex'],16),int(value['denominator_hex'],16))
 return F(*value)
