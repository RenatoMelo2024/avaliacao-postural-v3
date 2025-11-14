# Use a imagem base oficial do Python
FROM python:3.11-slim

# Instala as dependências do sistema necessárias para o OpenCV/MediaPipe
# O pacote libgl1 libsm6 libxext6 libpq-dev build-essential fornece o libGL.so.1, resolvendo o erro de importação.
RUN apt-get update && apt-get install -y \
    libgl1 libsm6 libxext6 libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho no contêiner
WORKDIR /app\n\n# Adiciona o diretório raiz do projeto ao PYTHONPATH\nENV PYTHONPATH=/app

# Copia os arquivos de dependências do Python
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da sua aplicação
COPY . .

# Expõe a porta que sua aplicação usa (5000 é o padrão para Flask/Gunicorn)
EXPOSE 5000

# Comando para iniciar a aplicação, baseado no Procfile original
# web: gunicorn --chdir backend/src main:app
CMD ["gunicorn", "--chdir", "backend/src", "main:app"]
