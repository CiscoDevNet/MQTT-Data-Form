FROM python:alpine

RUN apk update

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY templates /templates
COPY static /static

EXPOSE 5656

CMD ["python", "app.py"]
