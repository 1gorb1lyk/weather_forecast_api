# Weather API project for cities
## Developed on FastAPI with Poetry, AWS S3 and DynamoDB.

___
This project is a FastAPI application packaged with Docker, utilizing Poetry for dependency management. It includes support for caching weather data in S3 and logs events to DynamoDB.

## Necessary Tools:
To start the project, you need the following tools:

- Poetry;
- Docker;
- A `.env` file containing the required environment variables (explained below).

### Env file variables
In the project's root directory, create a `.env` file and define the following environment variables:

```
aws_access_key=<your-aws-access-key> - (str type)
aws_secret_key=<your-aws-secret-key> - (str type)
aws_region_name=<your-aws-s3-region> - (str type)
s3_bucket_name=<your-s3-bucket-name> - (str type)
cache_expiry_minutes=<cache-expiry-in-minutes> - (int type)
weather_api_key=<your-weather-api-key> - (str type)
dynamodb_table_name=weather_logs - (str type)
```

## Build and Run
### 1. Build and Run via Docker:
In your project terminal, run this command for building docker-compose:

```bash
docker-compose up --build
```

This command will:
- Build the Docker image based on the provided `Dockerfile`.
- Run the FastAPI app in the container, exposing it on port 8001.

Once the container is running, you can access the FastAPI server at `http://localhost:8001`.

### 2. Build and Run the app locally
If you want to run the project locally, without Docker, you need to follow the next steps:

1. Install dependencies using Poetry:

```bash
poetry install
```

2. Run the FastAPI application:

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Request for a test project

```http
GET http://localhost:8001/weather/?city={city}
```

Replace `{city}` with the name of the city for which you want to retrieve weather information.

Example: http://localhost:8001/weather/?city=Paris