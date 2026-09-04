# base Image
FROM python:3.14-slim

# Directory for docker. 
WORKDIR /app

# Copy code from working directory into docker file. 
COPY . .

# install requirements. 
RUN pip install --no-cache-dir .

# Allows you to run FLASK_APP instead of --app media_api.app or 
ENV FLASK_APP=media_api.app

# Allow traffic at 5000 port
EXPOSE 5000

# Commit database changes in migration folder -> run flask app in container. 
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=5000"]