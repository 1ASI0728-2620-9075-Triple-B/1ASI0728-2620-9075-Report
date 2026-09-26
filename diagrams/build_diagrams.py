#!/usr/bin/env python3
"""Genera todos los diagramas del informe.

Uso (desde la raíz del repositorio):  python3 diagrams/build_diagrams.py [cap3|cap4]
Requiere Python 3 y Chromium/Google Chrome. Los HTML fuente quedan en diagrams/html/.
Los diagramas C4 se generan aparte desde architecture/workspace.dsl (ver architecture/README.md).
"""
import sys

import cap3
import cap4

targets = sys.argv[1:] or ['cap3', 'cap4']
if 'cap3' in targets:
    cap3.build()
if 'cap4' in targets:
    cap4.build()
