FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 2>&1 | tee pip_install.log
EXPOSE $PORT
CMD uvicorn app:app --host 0.0.0.0 --port $PORT