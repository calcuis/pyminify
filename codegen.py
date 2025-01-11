import warnings
from .code_gen import *
warnings.warn(
    'codegen module is deprecated. Please import code_gen module instead.'
    , DeprecationWarning, stacklevel=2)
