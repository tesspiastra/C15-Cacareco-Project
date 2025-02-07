# Dashboard Module

The `dashboard` module is responsible for configuring and running the streamlit dashboard. The dashboard includes a number of visualisations that are relevant to the health of the plants. The module also includes the terraform responsible for building the ECS task that will host the dashboard.

## Setup

1. Install Docker on your system. Ensure the docker daemon is running when attempting to dockerize.
2. Install and initialize terraform
3. Build terraform resources
```
terraform init
terraform plan # Preview changes
terraform apply
```
4. Run streamlit locally for testing
```
streamlit run dashboard.py
```

## Virtual Environment Installation
Install required libraries into a `venv`
```
pip install -r requirements.txt
```
Requirements:
- altair
- pandas
- streamlit
- pymssql
- python-dotenv
- boto3
- wheel

## Deployment
Requirements for deploying 
1. Running the terraform commands to create the required resources 
2. Create a remote ECR (name used within this project: `c15-cacareco-lmnh-plants-dashboard`)
3. Push the docker image to the remote ECR (using the commands provided by AWS).
