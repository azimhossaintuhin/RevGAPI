from pathlib import Path
from decouple import config
from fastapi_mail import ConnectionConfig
from jinja2 import Environment, FileSystemLoader


BASE_DIR = Path(__file__).resolve().parent.parent


conf = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME"),
    MAIL_PASSWORD=config("MAIL_PASSWORD"),
    MAIL_FROM=config("MAIL_FROM"),
    MAIL_PORT=config("MAIL_PORT", cast=int),
    MAIL_SERVER=config("MAIL_SERVER"),
    MAIL_STARTTLS=config("MAIL_STARTTLS", cast=bool),
    MAIL_SSL_TLS=config("MAIL_SSL_TLS", cast=bool),
    TEMPLATE_FOLDER=BASE_DIR / "templates",
)

template_env = Environment(loader=FileSystemLoader(BASE_DIR / "templates"))

def render_template(template_name: str, **kwargs) -> str:
    template = template_env.get_template(template_name)
    return template.render(**kwargs)
