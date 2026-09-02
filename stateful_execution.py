import ast
import builtins
import contextlib
import dill
import io
import json
import logging
import os
import sys
import traceback
from typing import Any, Dict, Optional

from. import action_log
from. import errors
from. import module_overrides

_STATE_FILE = '/tmp/python_resources/.session_state.pkl'
_DISABLE_DILL = True

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._stringio_out = io.StringIO()
        sys.stderr = self._stringio_err = io.StringIO()
        return self
    def __exit__(self, *args):
        self.extend([self._stringio_out.getvalue(), self._stringio_err.getvalue()])
        sys.stdout = self._stdout
        sys.stderr = self._stderr

def _patched_input(prompt=''):
    raise RuntimeError('input() is not supported in this environment')

def execute(code: str, globals_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    result = {'stdout': '', 'stderr': '', 'result': None, 'error': None, 'actions': None}

    if not _DISABLE_DILL and os.path.exists(_STATE_FILE):
        try:
            with open(_STATE_FILE, 'rb') as f:
                session_data = dill.load(f)
                globals_dict = session_data.get('globals', {})
        except: pass

    if globals_dict is None:
        globals_dict = {'__builtins__': builtins}

    builtins.input = _patched_input
    module_overrides.setup_module_overrides({})

    try:
        with Capturing() as output:
            tree = ast.parse(code, mode='exec')
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                last_expr = ast.Expression(tree.body[-1].value)
                exec(compile(ast.Module(tree.body[:-1], type_ignores=[]), '<stdin>', 'exec'), globals_dict)
                result['result'] = eval(compile(last_expr, '<stdin>', 'eval'), globals_dict)
            else:
                exec(code, globals_dict)

        result['stdout'] = output[0]
        result['stderr'] = output[1]

    except Exception as e:
        result['error'] = traceback.format_exc()

    if not _DISABLE_DILL:
        try:
            with open(_STATE_FILE, 'wb') as f:
                dill.dump({'globals': globals_dict}, f)
        except: pass

    result['actions'] = action_log.export_actions_to_json()
    return result
