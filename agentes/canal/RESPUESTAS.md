______________ ERROR collecting scripts/pruebas/test_t3_real.py _______________
scripts\pruebas\test_t3_real.py:11: in <module>
    s = importlib.util.module_from_spec(spec)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:841: in module_from_spec
    ???
E   AttributeError: 'NoneType' object has no attribute 'loader'
=========================== short test summary info ===========================
ERROR scripts/pruebas/test_aceptacion.py - FileNotFoundError: [WinError 2] El...
ERROR scripts/pruebas/test_enunciados.py
ERROR scripts/pruebas/test_espejo.py
ERROR scripts/pruebas/test_t2_real.py - AttributeError: 'NoneType' object has...
ERROR scripts/pruebas/test_t3_real.py - AttributeError: 'NoneType' object has...
!!!!!!!!!!!!!!!!!!! Interrupted: 5 errors during collection !!!!!!!!!!!!!!!!!!!
5 errors in 2.89s
