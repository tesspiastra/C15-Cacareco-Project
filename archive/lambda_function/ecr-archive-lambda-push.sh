source .env
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $ECR_NAME
docker build -t $LOCAL_NAME --platform="linux/amd64" --provenance=false .
docker tag $LOCAL_NAME:latest $ECR_URI
docker push $ECR_URI
