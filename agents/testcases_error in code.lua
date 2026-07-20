 run python docker_probe_syntax_error.pyshubham@DESKTOP-K1MUEP0:/mnt/d/self-improving-dev-team_Autogen$ uv run python docker_probe_syntax_error.py
============================================================
OUTER exit_code: 0
OUTER output: WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.

[notice] A new release of pip is available: 25.0.1 -> 26.1.2
[notice] To update, run: pip install --upgrade pip
PYTEST_EXIT_CODE: 2
PYTEST_STDOUT: ============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3.12
cachedir: .pytest_cache
rootdir: /workspace
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
_______________________ ERROR collecting broken_test.py ________________________
/usr/local/lib/python3.12/site-packages/_pytest/python.py:508: in importtestmodule
    mod = import_path(
/usr/local/lib/python3.12/site-packages/_pytest/pathlib.py:596: in import_path
    importlib.import_module(module_name)
/usr/local/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1387: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1331: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
/usr/local/lib/python3.12/site-packages/_pytest/assertion/rewrite.py:179: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/_pytest/assertion/rewrite.py:348: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/ast.py:52: in parse
    return compile(source, filename, mode, flags,
E     File "/workspace/broken_test.py", line 2
E       def add(a, b)
E                    ^
E   SyntaxError: expected ':'
=========================== short test summary info ============================
ERROR broken_test.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 1.06s ===============================

PYTEST_STDERR: