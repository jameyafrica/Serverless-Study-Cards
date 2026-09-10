import json
import boto3
import pytest
from moto import mock_aws
from app import lambda_handler

@mock_aws
def test_create_card_success():
    # Set up a fake DynamoDB table in memory
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    dynamodb.create_table(
        TableName='StudyCards',
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'},
            {'AttributeName': 'cardId', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {'AttributeName': 'cardId', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    event = {
        'body': json.dumps({
            'question': 'What is Lambda?',
            'answer': 'A serverless compute service',
            'deckName': 'AWS Basics',
            'userId': 'demo-user'
        })
    }

    result = lambda_handler(event, None)

    assert result['statusCode'] == 201
    body = json.loads(result['body'])
    assert body['question'] == 'What is Lambda?'

@mock_aws
def test_create_card_missing_fields():
    event = {'body': json.dumps({'question': 'Only a question'})}
    result = lambda_handler(event, None)
    assert result['statusCode'] == 400