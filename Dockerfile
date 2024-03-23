FROM python:3.10

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN pip install -e .

ENTRYPOINT ["gpt-neteng"]
