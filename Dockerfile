FROM ubuntu:16.04
LABEL maintainer "Vichara Wijetunga"
RUN mkdir /app
COPY . app/
WORKDIR /app
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential libssl-dev libffi-dev libpq-dev
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_ENV="docker"
EXPOSE 80
RUN chmod +x entrypoint.sh
CMD ["entrypoint.sh"]
