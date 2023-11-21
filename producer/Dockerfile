FROM python:3.10.12

RUN pip install pipenv

WORKDIR /app

COPY . .

RUN pipenv install --system --deploy --ignore-pipfile

CMD ["python","src/FinnhubProducer.py"]