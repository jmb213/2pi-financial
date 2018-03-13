FROM python:3.6

ARG SERVER_PORT

# Define environment variable
ENV ENV 'development'
ENV SERVER_PORT $SERVER_PORT
ENV DATABASE_URL 'sqlite:////base/data/app.db'
ENV SECRET_KEY '9Sz8DPDmW3J3ue'

# Set the working directory to /app
WORKDIR /base

RUN apt-get install -y libpq-dev libsqlite3-dev

# Install any needed packages specified in requirements
ADD requirements.txt /etc/requirements.txt
RUN pip install --trusted-host pypi.python.org -r /etc/requirements.txt

# Make port available to the world outside this container
EXPOSE $SERVER_PORT

# Run app.py when the container launches
CMD ["python", "runserver.py"]
