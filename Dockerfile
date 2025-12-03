FROM python:3.12-slim
RUN apt update

RUN apt install -y --no-install-recommends curl gcc g++ gnupg unixodbc-dev unixodbc

# If using pyodbc and you need to build from source, you might also need:
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app
COPY . /app
ENTRYPOINT ["python", "main.py"]
