# Use adoptopenjdk image as builder
FROM adoptopenjdk:11-jdk-hotspot as builder

# Use debian sid image
FROM debian:sid
COPY ./ /bmw_code_agent/
WORKDIR /bmw_code_agent

# Install python3, pip and dependencies
RUN apt-get -y update
RUN apt-get -y dist-upgrade
#RUN apt-get install wget build-essential libreadline-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
RUN apt-get install -y python3-full
RUN apt-get install -y python3-pip

# Install git
RUN apt-get -y install git

# Install python dependencies
RUN python3 -m venv /venv
RUN /venv/bin/pip3 install -r requirements.txt
EXPOSE 5000

# Copy und install certificates
COPY ./assets/BMW_Trusted_Certificates_V16/Intermediate/*.crt /usr/local/share/ca-certificates/
COPY ./assets/BMW_Trusted_Certificates_V16/Root/*.crt /usr/local/share/ca-certificates/
RUN apt-get -y install openssl
RUN echo -n | openssl s_client -connect gcdm-ai-emea-poc.openai.azure.com:443 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /usr/local/share/ca-certificates/gcdm-ai-emea-poc.crt

# Update CA certificates
RUN update-ca-certificates

# Remove Git configurations (if they exist)
RUN git config --global --get "remote.origin.url" && git config --global --unset "remote.origin.url" || true && \
    git config --global --get "http.https://github.com/.extraheader" && git config --global --unset "http.https://github.com/.extraheader" || true && \
    git config --local --get "remote.origin.url" && git config --local --unset "remote.origin.url" || true && \
    git config --local --get "http.https://github.com/.extraheader" && git config --local --unset "http.https://github.com/.extraheader" || true

# Copy Java from builder
COPY --from=builder /opt/java/openjdk /opt/java/openjdk

# Set environment variable JAVA_HOME
ENV JAVA_HOME=/opt/java/openjdk
# Add Java binaries to PATH
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install pmd for java code analysis
RUN apt-get -y install wget
RUN apt-get -y install wget unzip
RUN wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.0.0-rc4/pmd-dist-7.0.0-rc4-bin.zip
RUN unzip pmd-dist-7.0.0-rc4-bin.zip

# Set the script as the default command
CMD ["/venv/bin/python3", "-m", "controller.src.api.primary_api"]