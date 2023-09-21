FROM python:3.12.0rc2

COPY dist/*.whl /

RUN pip install /*.whl && rm /*.whl

WORKDIR /workspace
