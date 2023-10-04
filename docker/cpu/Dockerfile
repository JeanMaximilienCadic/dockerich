FROM python:3.11.5

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
