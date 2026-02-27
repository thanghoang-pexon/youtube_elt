ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.10

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ENV AIRFLOW_HOME=/opt/airflow

# copy requirements into the airflow home so the subsequent RUN can
# reference the file from the default working directory (/opt/airflow)
COPY requirements.txt ${AIRFLOW_HOME}/

# install both the explicit Airflow version (the base image already has
# it, but pinning again is harmless) and any extra requirements
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" \
    -r ${AIRFLOW_HOME}/requirements.txt
