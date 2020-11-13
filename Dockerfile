# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR .
COPY . .

# install dependencies
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg -y

# Open port
EXPOSE 8000

# command to run on container start
CMD [ "python", "./main.py" ]
