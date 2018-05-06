FROM python:3.6-alpine
COPY requirements.txt /
RUN mkdir /data 
RUN pip install -r /requirements.txt
COPY src/ /app
WORKDIR /app
CMD ["python", "./main.py"]