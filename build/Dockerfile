# Use uma imagem base oficial do Python
FROM python:3.10

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie os arquivos de requisitos para o container
COPY requirements.txt .

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código para o container
COPY . .

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]