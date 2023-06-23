FROM python:3.12.0b3

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
