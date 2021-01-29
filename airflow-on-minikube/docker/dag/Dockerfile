FROM localhost:5000/base

ARG AIRFLOW_HOME=/usr/local/airflow
ARG AIRFLOW_USER=airflow
ENV PATH "${AIRFLOW_HOME}:${PATH}"
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

RUN mkdir ${AIRFLOW_HOME}/tmp

# Install Python Dag Deps into virtualenv
COPY requirements.txt .
RUN . ${AIRFLOW_HOME}/venv/bin/activate && pip install -r requirements.txt
RUN rm -rf requirements.txt /root/.cache

# Deploy dags into airflow dags folder
COPY ./airflow_dags ${AIRFLOW_HOME}/dags
COPY ./ci ${AIRFLOW_HOME}/ci
COPY example ${AIRFLOW_HOME}/example
COPY ./project ${AIRFLOW_HOME}/project

RUN chmod 755 ${AIRFLOW_HOME}/example/basic_test.py
RUN chmod 755 ${AIRFLOW_HOME}/ci/launch_ingest.sh
RUN chmod 755 ${AIRFLOW_HOME}/project

RUN chown -R ${AIRFLOW_USER}:${AIRFLOW_USER} ${AIRFLOW_HOME}
WORKDIR ${AIRFLOW_HOME}
EXPOSE 8080
EXPOSE 8793
