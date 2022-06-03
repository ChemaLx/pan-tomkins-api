FROM python:3.8.6

WORKDIR /user/src/app

ADD app.py .

RUN pip install -r 