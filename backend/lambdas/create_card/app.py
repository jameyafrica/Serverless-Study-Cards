import json          # Built-in Python library — converts between JSON strings and Python dicts
import uuid          # Built-in Python library — generates random unique IDs
import time          # Built-in Python library — lets us get the current timestamp
import boto3         # AWS's official Python SDK — how Python code talks to AWS services

# --- Connect to DynamoDB ---
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table('StudyCards')

def lambda_handler(event, context):
    try:
        # --- Step 1: Parse the incoming request body ---
        body = json.loads(event.get('body', '{}'))

        # --- Step 2: Extract the fields we care about ---
        question = body.get('question')
        answer = body.get('answer')
        deck_name = body.get('deckName', 'default')
        user_id = body.get('userId', 'demo-user')

        # --- Step 3: Validate required fields exist ---
        if not question or not answer:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'question and answer are required'})
            }

        # --- Step 4: Build the item to store ---
        card = {
            'userId': user_id,
            'cardId': str(uuid.uuid4()),
            'question': question,
            'answer': answer,
            'deckName': deck_name,
            'createdAt': int(time.time())
        }

        # --- Step 5: Save it to DynamoDB ---
        table.put_item(Item=card)

        # --- Step 6: Return success response ---
        return {
            'statusCode': 201,
            'body': json.dumps(card)
        }

    except Exception as e:
        # --- Catch-all: something unexpected broke ---
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }