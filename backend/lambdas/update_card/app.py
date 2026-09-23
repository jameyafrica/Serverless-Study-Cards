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

    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }

    question = body.get('question')
    answer = body.get('answer')

    if not question and not answer:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'At least one of question or answer is required'})
        }

    update_parts = []
    expression_values = {}

    if question:
        update_parts.append('question = :q')
        expression_values[':q'] = question

    if answer:
        update_parts.append('answer = :a')
        expression_values[':a'] = answer

    update_expression = 'SET ' + ', '.join(update_parts)

    table.update_item(
        Key={'userId': user_id, 'cardId': card_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Card updated successfully'})
    }