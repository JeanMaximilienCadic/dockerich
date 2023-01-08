FROM python:3.11.1

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
