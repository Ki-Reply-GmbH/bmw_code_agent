FROM python:3.11-slim
COPY ./ /ki_repy_merge_conflict_resolver/
WORKDIR /ki_repy_merge_conflict_resolver
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
CMD ["python3", "src/main.py"]