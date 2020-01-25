FROM base
WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD . /app
ENV FLASK_ENV="docker"
EXPOSE 5000
RUN chmod +x entrypoint.sh
CMD ["entrypoint.sh"]
