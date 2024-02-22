FROM python:3.13.0a4

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
