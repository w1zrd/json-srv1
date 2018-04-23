FROM python:3.6.4-alpine3.7
WORKDIR /usr/src/app
RUN pip install pip --upgrade && pip install --no-cache flask flask-httpauth jsonify
ADD *.py ./
CMD [ "python", "./main.py" ]
