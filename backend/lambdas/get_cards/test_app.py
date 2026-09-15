import json
import boto3
import pytest
from moto import mock_aws
from app import lambda_handler

@mock_aws
def test_get_cards_returns_items():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.create_table(
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

    table.put_item(Item={'userId': 'demo-user', 'cardId': 'test-1', 'question': 'What is DynamoDB?', 'answer': 'A NoSQL database'})
    table.put_item(Item={'userId': 'demo-user', 'cardId': 'test-2', 'question': 'What is IAM?', 'answer': 'Identity and Access Management'})

    event = {'pathParameters': {'userId': 'demo-user'}}
    result = lambda_handler(event, None)

    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert len(body) == 2


@mock_aws
def test_get_cards_missing_user_id():
    event = {'pathParameters': {}}
    result = lambda_handler(event, None)
    assert result['statusCode'] == 400