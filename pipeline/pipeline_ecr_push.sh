aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com
docker build -t c15-cacareco-lmnh-plants-etl .
docker tag c15-cacareco-lmnh-plants-etl:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c15-cacareco-lmnh-plants-etl:latest
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c15-cacareco-lmnh-plants-etl:latest