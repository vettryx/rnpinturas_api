# Usa a versão exata do Python que você definiu no Poetry
FROM python:3.14

# Instala as dependências do sistema operacional para o WeasyPrint funcionar (Cairo, Pango, etc)
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Configura o ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho dentro do contêiner
WORKDIR /app

# Instala o Poetry
RUN pip install poetry

# Copia os arquivos de configuração do Poetry
COPY pyproject.toml ./

# Configura o Poetry para não criar virtualenv (no Docker não precisa) e instala as dependências
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

# Copia o resto do código do projeto
COPY . .

# Coleta os arquivos estáticos (o WhiteNoise vai usar isso)
RUN python manage.py collectstatic --noinput

# Inicia o servidor com o Gunicorn que você já colocou no seu pyproject.toml
# O Render injeta a porta na variável $PORT automaticamente
CMD gunicorn rnpinturas.wsgi:application --bind 0.0.0.0:${PORT:-10000}