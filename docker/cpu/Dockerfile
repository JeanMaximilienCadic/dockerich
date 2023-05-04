FROM python:3.10.11

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
