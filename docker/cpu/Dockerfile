FROM python:3.12.0rc1

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
