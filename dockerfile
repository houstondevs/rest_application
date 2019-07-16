FROM python:3
RUN mkdir src/
COPY . /src
WORKDIR /src/
RUN pip install -r requirements.txt
