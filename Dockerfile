FROM python:3.8.2

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .