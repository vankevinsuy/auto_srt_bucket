FROM python:3.11.4

WORKDIR app

COPY main.py .
COPY requirements.txt .

RUN mkdir bucket

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
