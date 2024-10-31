FROM python:3.11.9

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install poetry
RUN pip install poetry

COPY . /app/

# Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi


CMD ["poetry", "run", "gunicorn", "--certfile=certificates/localhost.pem", "--keyfile=certificates/localhost-key.pem", "--bind", "0.0.0.0:8000", "djangoapp.wsgi:application"]


