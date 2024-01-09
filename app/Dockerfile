# syntax=docker/dockerfile:1
FROM python:3.8-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENV PORT 8080
EXPOSE 8080
ENTRYPOINT ["python", "application.py"]