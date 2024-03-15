FROM python:3.11
COPY ./ /bmw_code_agent/
WORKDIR /bmw_code_agent

#ARG OPENAI_API_KEY
#ARG GIT_USERNAME
#ARG GIT_ACCESS_TOKEN
#ARG GIT_WEBHOOK_SECRET
#ARG MONITORED_REPO

#ENV OPENAI_API_KEY=$OPENAI_API_KEY
#ENV GIT_USERNAME=$GIT_USERNAME
#ENV GIT_ACCESS_TOKEN=$GIT_ACCESS_TOKEN
#ENV GIT_WEBHOOK_SECRET=$GIT_WEBHOOK_SECRET
#ARG MONITORED_REPO=$MONITORED_REPO

# Install dependencies
RUN apt-get -y update
RUN apt-get -y install git
RUN pip3 install -r requirements.txt
EXPOSE 5000

# Copy und isntall certificates
COPY ./assets/BMW_Trusted_Certificates_V16/Intermediate/*.crt /usr/local/share/ca-certificates/
COPY ./assets/BMW_Trusted_Certificates_V16/Root/*.crt /usr/local/share/ca-certificates/
RUN apt-get -y install openssl
RUN echo -n | openssl s_client -connect gcdm-ai-emea-poc.openai.azure.com:443 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /usr/local/share/ca-certificates/gcdm-ai-emea-poc.crt

# Update CA certificates
RUN update-ca-certificates

# Install pmd for java code analysis
RUN wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.0.0-rc4/pmd-dist-7.0.0-rc4-bin.zip
RUN unzip pmd-dist-7.0.0-rc4-bin.zip
CMD ["python3", "-m", "controller.src.webhooks.api"]