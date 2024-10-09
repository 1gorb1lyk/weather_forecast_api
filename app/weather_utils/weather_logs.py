import json

import aioboto3
from dotenv import load_dotenv
from app.config import settings
from datetime import datetime
import uuid
from io import BytesIO

load_dotenv()


async def dynamodb_logs(city: str, s3_link: str):

    timestamp = datetime.now().isoformat()
    dynamo_table_name = settings.dynamodb_table_name

    async with aioboto3.Session().client(
        'dynamodb',
        aws_access_key_id=settings.aws_access_key,
        aws_secret_access_key=settings.aws_secret_key,
        region_name=settings.aws_region_name
    ) as dynamodb_client:
        await dynamodb_client.put_item(
            TableName=dynamo_table_name,
            Item={
                'log_id': {'S': str(uuid.uuid4())},
                'city': {'S': city},
                'timestamp': {'S': timestamp},
                's3_url': {'S': s3_link}
            }
        )


async def json_to_s3(weather_cache_key: str, data: dict):

    json_data = json.dumps(data)
    byte_data = BytesIO(json_data.encode('utf-8'))

    async with aioboto3.Session().client(
        's3',
        aws_access_key_id=settings.aws_access_key,
        aws_secret_access_key=settings.aws_secret_key,
        region_name=settings.aws_region_name
    ) as s3_client:
        await s3_client.upload_fileobj(byte_data, settings.s3_bucket_name, weather_cache_key)
