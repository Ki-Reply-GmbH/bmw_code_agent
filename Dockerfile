FROM python:3.11
COPY ./ /bmw_code_agent/
WORKDIR /bmw_code_agent

ARG OPENAI_API_KEY
ARG GIT_USERNAME
ARG GIT_ACCESS_TOKEN
ARG GIT_WEBHOOK_SECRET

ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV GIT_USERNAME=$GIT_USERNAME
ENV GIT_ACCESS_TOKEN=$GIT_ACCESS_TOKEN
ENV GIT_WEBHOOK_SECRET=$GIT_WEBHOOK_SECRET

# Install dependencies
RUN apt-get -y update
RUN apt-get -y install git
RUN git config --global user.email "t.kubera@reply.de"
RUN git config --global user.name "Timo Kubera"
RUN pip3 install -r requirements.txt

# Install pmd for java code analysis
RUN wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.0.0-rc4/pmd-dist-7.0.0-rc4-bin.zip
RUN unzip pmd-dist-7.0.0-rc4-bin.zip
CMD ["python3", "-m", "controller.src.main"]
# Mit Davide sprechen wegen Open AI API key
# Reply Mail Adresse verwenden, nicht private