import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table('StudyCards')

def lambda_handler(event, context):
    # Get userId from the path parameters (e.g. /cards/demo-user)
    user_id = event.get('pathParameters', {}).get('userId')

    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'userId is required'})
        }

    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id)
    )

    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }