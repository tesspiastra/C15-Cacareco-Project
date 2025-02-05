# C15-Cacareco-Project

There are three stages of this project:
1. The pipeline
2. Archive Management
3. Dashboard 

In this README.md you will find the background setup needed to run this project on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Installation 

Key Softwares used in this project:
- Docker: [Install docker].(https://docs.docker.com/desktop/) based on your machine
- Homebrew: [install instructions].(https://brew.sh/)
- Terraform: You can use [brew commands].(https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) to install Terraform

#### Python Libraries

This project has several requirement files, all of which are included in their respective Docker images.

If docker is not being used, you can run ```pip3 install -r``` requirements.txt in each folder

### Set up

In order to build the docker images, run:
```docker build -t name-tag:latest --platform "linux/amd64" . ```
With a different tag for each of the three images.

### Testing TODO

How we did our testing and how to run the tests yourself.

### Deployment TODO

Add additional notes about how to deploy this on a live system
