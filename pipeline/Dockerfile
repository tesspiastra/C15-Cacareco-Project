FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt 

COPY pipeline.py .

COPY logger_config.py .

CMD [ "pipeline.handler" ]
