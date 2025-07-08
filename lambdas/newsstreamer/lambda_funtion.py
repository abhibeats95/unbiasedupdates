import boto3
import json
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr

# Constants
TABLE_NAME = "news_articles"
DAYS_BACK = 7  # Articles from the last 7 days

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Calculate the threshold date
        now = datetime.utcnow()
        threshold_date = now - timedelta(days=DAYS_BACK)

        # Scan the table with a filter on 'publisheddate'
        response = table.scan(
            FilterExpression=Attr('publisheddate').gte(threshold_date.isoformat())
        )
        items = response.get('Items', [])

        # Return items as JSON response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS for UI access
            },
            'body': json.dumps(items)
        }

    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }