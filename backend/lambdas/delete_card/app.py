import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table('StudyCards')

def lambda_handler(event, context):
    path_params = event.get('pathParameters') or {}
    card_id = path_params.get('cardId')

    # TODO: replace with real authenticated user ID once login/auth exists.
    # No auth system yet — single hardcoded user for now (matches project scope).
    user_id = 'demo-user'

    if not card_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cardId is required'})
        }

    table.delete_item(
        Key={'userId': user_id, 'cardId': card_id}
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Card deleted successfully'})
    }