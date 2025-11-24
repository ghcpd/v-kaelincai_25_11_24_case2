FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"
CMD ["python", "tests/test_runner.py"]
