import os
import sys

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # a Vercel importa este arquivo sem src/ no caminho

from agendafacil import create_app  # noqa: E402

app = create_app()
