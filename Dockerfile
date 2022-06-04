FROM python:3.8.6

ADD . . 

COPY './requirements.txt' .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "app.py" ]