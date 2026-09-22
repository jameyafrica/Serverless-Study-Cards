import json
import boto3
import pytest
from moto import mock_aws

from update_card.app import lambda_handler


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
def test_update_card_success():
    table = _make_table()
    table.put_item(Item={
        'userId': 'demo-user',
        'cardId': 'test-1',
        'question': 'Old question',
        'answer': 'Old answer'
    })

    event = {
        'pathParameters': {'userId': 'demo-user', 'cardId': 'test-1'},
        'body': json.dumps({'question': 'New question', 'answer': 'New answer'})
    }
    result = lambda_handler(event, None)

    assert result['statusCode'] == 200

    updated_item = table.get_item(Key={'userId': 'demo-user', 'cardId': 'test-1'})['Item']
    assert updated_item['question'] == 'New question'
    assert updated_item['answer'] == 'New answer'


@mock_aws
def test_update_card_partial_update_keeps_other_field():
    table = _make_table()
    table.put_item(Item={
        'userId': 'demo-user',
        'cardId': 'test-1',
        'question': 'Old question',
        'answer': 'Old answer'
    })

    event = {
        'pathParameters': {'userId': 'demo-user', 'cardId': 'test-1'},
        'body': json.dumps({'question': 'Only question changed'})
    }
    result = lambda_handler(event, None)

    assert result['statusCode'] == 200

    updated_item = table.get_item(Key={'userId': 'demo-user', 'cardId': 'test-1'})['Item']
    assert updated_item['question'] == 'Only question changed'
    assert updated_item['answer'] == 'Old answer'


@mock_aws
def test_update_card_missing_ids():
    event = {
        'pathParameters': {},
        'body': json.dumps({'question': 'New question'})
    }
    result = lambda_handler(event, None)
    assert result['statusCode'] == 400


@mock_aws
def test_update_card_no_fields_to_update():
    event = {
        'pathParameters': {'userId': 'demo-user', 'cardId': 'test-1'},
        'body': json.dumps({})
    }
    result = lambda_handler(event, None)
    assert result['statusCode'] == 400