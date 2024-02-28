FROM python:3.11-slim
COPY ./ /ki_reply_code_quality_agent/
WORKDIR /ki_reply_code_quality_agent
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY

RUN pip3 install -r requirements.txt
CMD ["python3", "src/main.py"]