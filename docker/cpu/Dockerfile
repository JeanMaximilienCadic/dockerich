FROM python:3.6

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
