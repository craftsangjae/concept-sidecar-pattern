FROM python:3.11



# Install MinIO Client
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/bin

WORKDIR /app
COPY pyproject.toml README.md main.py ./

# Set the working directory
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev


ENTRYPOINT ["python", "main.py"]