FROM python:3.8.18

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
