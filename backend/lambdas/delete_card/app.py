import json
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table('StudyCards')

def lambda_handler(event, context):
    path_params = event.get('pathParameters') or {}
    user_id = path_params.get('userId')
    card_id = path_params.get('cardId')

    if not user_id or not card_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'userId and cardId are required'})
        }

    table.delete_item(
        Key={'userId': user_id, 'cardId': card_id}
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Card deleted successfully'})
    }