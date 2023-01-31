# Set base image (host OS)
FROM python:3.11-alpine

# By default, listen on port 5000
#EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /flasksearch


# Copy the dependencies file to the working directory
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# Install any dependencies
#RUN pip install -r requirements.txt

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# Copy the content of the local src directory to the working directory
