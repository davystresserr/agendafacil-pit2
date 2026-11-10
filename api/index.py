"""Ponto de entrada da Vercel: expõe o app Flask (WSGI) de src/wsgi.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from wsgi import app  # noqa: E402,F401
