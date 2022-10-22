FROM python:3.10.7

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
