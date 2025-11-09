import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
import boto3

def lambda_handler(event, context):
    # --- Environment variables ---
    api_key = os.environ.get('YOUTUBE_API_KEY')
    bucket_name = os.environ.get('S3_BUCKET_NAME', '').strip()

    if not api_key or not bucket_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing YOUTUBE_API_KEY or S3_BUCKET_NAME environment variable'})
        }

    # --- YouTube API endpoint ---
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'snippet,contentDetails,statistics',
        'chart': 'mostPopular',
        'maxResults': 50,
        'regionCode': 'US',  # change region if desired
        'key': api_key
    }

    # Build URL
    full_url = f"{url}?{urllib.parse.urlencode(params)}"

    # --- Call YouTube API ---
    try:
        with urllib.request.urlopen(full_url) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

    # --- Convert to JSON ---
    json_data = json.dumps(data, indent=2)

    # --- S3 Upload Path ---
    s3 = boto3.client('s3')
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    key = f"raw_data/youtube_trending_{timestamp}.json"

    # --- Upload to S3 ---
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json_data,
        ContentType='application/json'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'YouTube trending data extracted successfully',
            's3_path': f"s3://{bucket_name}/{key}"
        })
    }
