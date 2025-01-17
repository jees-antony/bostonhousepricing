FROM ultralytics/ultralytics:latest-python
COPY . /app
WORKDIR /app
# RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt 2>&1 | tee pip_install.log
EXPOSE $PORT
CMD uvicorn app:app --host 0.0.0.0 --port $PORT