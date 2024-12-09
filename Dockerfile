FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY src .

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
