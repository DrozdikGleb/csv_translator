FROM python:3.10.6-slim

RUN apt-get update && apt-get -y install gcc

RUN pip install poetry

WORKDIR /app

COPY . /app

# Install dependencies
RUN poetry lock
RUN poetry install

CMD [ "poetry", "run", "streamlit", "run", "./csv_translator/main.py" ]