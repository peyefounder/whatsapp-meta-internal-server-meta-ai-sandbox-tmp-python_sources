import sys
import builtins
from. import errors

BLOCKED_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'shutil', 'glob',
    'multiprocessing', 'threading', 'ctypes', 'dill', 'requests'
}

_original_import = builtins.__import__

def _custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    root_name = name.split('.')[0]
    if root_name in BLOCKED_MODULES:
        raise errors.ModuleNotAllowedError(f"'{root_name}' is not available on this platform")
    return _original_import(name, globals, locals, fromlist, level)

def setup_module_overrides(config):
    builtins.__import__ = _custom_import 
