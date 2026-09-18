import json
import boto3
import pytest
from moto import mock_aws
from app import lambda_handler


def _make_table():
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
    return table


@mock_aws
def test_delete_card_success():
    table = _make_table()
    table.put_item(Item={
        'userId': 'demo-user',
        'cardId': 'test-1',
        'question': 'What is DynamoDB?',
        'answer': 'A NoSQL database'
    })

    event = {'pathParameters': {'userId': 'demo-user', 'cardId': 'test-1'}}
    result = lambda_handler(event, None)

    assert result['statusCode'] == 200

    # Confirm the item is actually gone
    response = table.get_item(Key={'userId': 'demo-user', 'cardId': 'test-1'})
    assert 'Item' not in response


@mock_aws
def test_delete_card_only_removes_target_item():
    table = _make_table()
    table.put_item(Item={'userId': 'demo-user', 'cardId': 'test-1', 'question': 'Q1', 'answer': 'A1'})
    table.put_item(Item={'userId': 'demo-user', 'cardId': 'test-2', 'question': 'Q2', 'answer': 'A2'})

    event = {'pathParameters': {'userId': 'demo-user', 'cardId': 'test-1'}}
    lambda_handler(event, None)

    # test-1 should be gone, test-2 should remain
    response_1 = table.get_item(Key={'userId': 'demo-user', 'cardId': 'test-1'})
    response_2 = table.get_item(Key={'userId': 'demo-user', 'cardId': 'test-2'})
    assert 'Item' not in response_1
    assert 'Item' in response_2


@mock_aws
def test_delete_card_missing_ids():
    event = {'pathParameters': {}}
    result = lambda_handler(event, None)
    assert result['statusCode'] == 400


@mock_aws
def test_delete_card_nonexistent_item_still_succeeds():
    _make_table()  # empty table, nothing seeded

    event = {'pathParameters': {'userId': 'demo-user', 'cardId': 'does-not-exist'}}
    result = lambda_handler(event, None)

    # Matches DynamoDB's natural idempotent behavior, discussed above
    assert result['statusCode'] == 200