FROM python:3.11-slim
COPY ./ /bmw_code_agent/
WORKDIR /bmw_code_agent
ARG OPENAI_API_KEY
ARG GIT_USERNAME
ARG GIT_ACCESS_TOKEN
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV GIT_USERNAME=$GIT_USERNAME
ENV GIT_ACCESS_TOKEN=$GIT_ACCESS_TOKEN

RUN apt-get -y update
RUN apt-get -y install git
RUN git config --global user.email "timokubera@yahoo.com"
RUN git config --global user.name "Timo Kubera"
RUN pip3 install -r requirements.txt
CMD ["python3", "-m", "controller.src.main"]