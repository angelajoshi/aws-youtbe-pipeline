import json
import os
import io
from datetime import datetime
import boto3
import pandas as pd

def lambda_handler(event, context):
    bucket_name = os.environ.get('S3_BUCKET_NAME', '').strip()
    s3 = boto3.client('s3')

    # --- Step 1: Get latest raw_data file ---
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix='raw_data/')
    if 'Contents' not in response or not response['Contents']:
        return {'statusCode': 404, 'body': json.dumps({'error': 'No files found in raw_data/'})}

    latest = max(response['Contents'], key=lambda x: x['LastModified'])
    key = latest['Key']

    print(f"Processing file: {key}")

    # --- Step 2: Read JSON file ---
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    data = json.loads(obj['Body'].read().decode('utf-8'))

    items = data.get('items', [])
    if not items:
        return {'statusCode': 400, 'body': json.dumps({'error': 'No items found in JSON'})}

    # --- Step 3: Flatten JSON structure ---
    records = []
    for item in items:
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        content = item.get('contentDetails', {})

        records.append({
            'videoId': item.get('id'),
            'title': snippet.get('title'),
            'channelTitle': snippet.get('channelTitle'),
            'publishedAt': snippet.get('publishedAt'),
            'categoryId': snippet.get('categoryId'),
            'viewCount': stats.get('viewCount'),
            'likeCount': stats.get('likeCount'),
            'commentCount': stats.get('commentCount'),
            'duration': content.get('duration'),
            'definition': content.get('definition'),
            'caption': content.get('caption')
        })

    df = pd.DataFrame(records)

    # --- Step 4: Convert numeric fields ---
    numeric_cols = ['viewCount', 'likeCount', 'commentCount']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- Step 5: Write to Parquet in memory ---
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False)

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    parquet_key = f"processed_data/youtube_trending_{timestamp}.parquet"

    # --- Step 6: Upload to S3 ---
    s3.put_object(
        Bucket=bucket_name,
        Key=parquet_key,
        Body=parquet_buffer.getvalue(),
        ContentType='application/octet-stream'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Transformation complete — data saved as Parquet',
            'output': f"s3://{bucket_name}/{parquet_key}"
        })
    }
