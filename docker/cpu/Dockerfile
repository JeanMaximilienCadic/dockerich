FROM python:3.7.14

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
