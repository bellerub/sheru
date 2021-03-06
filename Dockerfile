FROM python:3.7-alpine as base

# Build psycopg2 from source
FROM base as builder
                                                                                                                              
RUN mkdir /install
RUN apk --update add \
        libffi-dev \
        postgresql-dev \
        gcc \
        python3-dev \
        musl-dev 
WORKDIR /install
RUN echo -e "psycopg2-binary\nchannels" > /requirements.txt && pip install --user -r /requirements.txt

FROM base

# Copy compiled python modules from other container
COPY --from=builder /root/.local /root/.local

# Setup Environment
ENV PYTHONUNBUFFERED 1

# Tmp Env Vars for Django to run
ENV DEBUG False
ENV DB_NAME 'postgre'
ENV DB_USER 'postgre'
ENV DB_PWD 'postgre'

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

RUN mkdir /project
WORKDIR /project

ADD ./project/package*.json /project/

# Install Packages
RUN apk --no-cache add libpq bash npm && \
    npm install

# Install dependencies via pip
ADD requirements.txt /project/
RUN pip install -r requirements.txt

ADD ./project/ /project/
ADD ./entrypoint.sh /project

ENTRYPOINT [ "./entrypoint.sh" ]