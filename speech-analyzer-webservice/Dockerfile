FROM python:3.9-slim-buster

RUN mkdir /root/.aws
WORKDIR /root/.aws

COPY credentials credentials
COPY config config

WORKDIR /opt/webapp

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY webapp .

EXPOSE 5001

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "-m", "007", "wsgi:app"]

