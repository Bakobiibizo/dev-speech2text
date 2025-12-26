FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip     && pip install setuptools wheel

WORKDIR /app

COPY . /app/

EXPOSE 4900:4900

RUN pip install -r requirements.txt

CMD ["python", "run_api.py"]
