from dotenv import load_dotenv

load_dotenv()

from agendafacil import create_app  # noqa: E402

app = create_app()
