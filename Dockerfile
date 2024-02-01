FROM python:3.11.5
ENV PYTHONUNBUFFERED=1
WORKDIR /alemeno
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt



