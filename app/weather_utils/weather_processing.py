import time
import json
import aioboto3
import aiohttp

from aiohttp import ClientError
from dotenv import load_dotenv
from fastapi import HTTPException, status
from app.config import settings
from datetime import datetime, timezone, timedelta
from .weather_logs import dynamodb_logs, json_to_s3

load_dotenv()


class WeatherProcessing:

    def __init__(self, city: str):
        self.city = city

    async def get_city_weather_data(self) -> dict:
        timestamp = time.time()
        weather_cache_key = f"{self.city}_{timestamp}.json"

        async with aioboto3.Session().client(
                's3',
                aws_access_key_id=settings.aws_access_key,
                aws_secret_access_key=settings.aws_secret_key,
                region_name=settings.aws_region_name
        ) as s3_client:
            try:
                s3_object = await s3_client.list_objects(Bucket=settings.s3_bucket_name, Prefix=self.city)

                if 'Contents' in s3_object:
                    current_time = datetime.now(timezone.utc)
                    last_updated = s3_object['Contents'][-1]['LastModified']

                    if current_time - last_updated < timedelta(minutes=settings.cache_expiry_minutes):
                        s3_response = await s3_client.get_object(
                            Bucket=settings.s3_bucket_name,
                            Key=s3_object['Contents'][0]['Key']
                        )

                        cached_data = await s3_response['Body'].read()
                        return json.loads(cached_data.decode('utf-8'))
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '403':
                    raise HTTPException(detail='Access was denied for this client. Update .env dependencies or check '
                                               'AWS S3 access', status_code=status.HTTP_403_FORBIDDEN)
                elif error_code == '404':
                    raise HTTPException(detail=f"Cache not found for city -> {self.city}",
                                        status_code=status.HTTP_404_NOT_FOUND)
                else:
                    raise HTTPException(detail=f"Error during execution -> {e.response['Error']['Message']}",
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        weather_data = await self.__request_to_weather_api()

        await json_to_s3(weather_cache_key, weather_data)
        await dynamodb_logs(self.city, f"s3://{settings.s3_bucket_name}/{weather_cache_key}")

        return weather_data

    async def __request_to_weather_api(self):
        api_key = settings.weather_api_key
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={self.city}&aqi=yes'

        headers = {
            'User-Agent':
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
        }

        async with aiohttp.ClientSession() as request:
            async with request.get(url=url, headers=headers) as response:
                if response.status != 200:
                    error = await response.json()

                    raise HTTPException(detail=f"Error fetching weather data via API -> {error['error']['message']}",
                                        status_code=response.status)

                weather_response = await response.json()

        return weather_response
