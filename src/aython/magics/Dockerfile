FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /root/.jupyter

# Copy Jupyter configuration
COPY app/jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

EXPOSE 8888

CMD ["python", "/app/start_jupyter.py"]
