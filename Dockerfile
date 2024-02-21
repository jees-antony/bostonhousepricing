FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 2>&1 | tee pip_install.log
EXPOSE $PORT
CMD gunicorn --workers=4 --bind 0.0.0.0:$PORT app:app