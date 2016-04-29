# Dockerfile example taken from https://docs.docker.com/compose/django/
FROM python:2.7

# Ensure that Python outputs everything that's printed inside # the application
# rather than buffering it.
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

# Install node and npm
RUN apt-get update && \
  apt-get install -y --no-install-recommends nodejs npm;

# install node modules
RUN npm install less yuglify
# create a symbolic link for node
RUN ln -s /usr/bin/nodejs /usr/bin/node

# Create the required env and settings files
COPY oneanddone/settings/local.py-dist oneanddone/settings/local.py

# Start the development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
