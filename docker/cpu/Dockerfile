FROM python:3.10.12

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
