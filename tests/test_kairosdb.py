import pytest
from examon.db.kairosdb import KairosDB
import gzip
import json

def test_kairosdb_initialization():
    client = KairosDB('localhost', '8080', 'user', 'pass')
    assert client.server == 'localhost'
    assert client.port == '8080'
    assert client.user == 'user'
    assert client.password == 'pass'

def test_put_metrics(mock_requests_session):
    client = KairosDB('localhost', '8080')
    metrics = [
        {
            'name': 'test.metric',
            'timestamp': 1234567890000,
            'value': 42,
            'tags': {'host': 'test-host'}
        }
    ]
    
    client.put_metrics(metrics)
    
    # Verify the POST request was made once with the correct arguments
    mock_requests_session.return_value.post.assert_called_once_with(
        'http://localhost:8080/api/v1/datapoints',
        gzip.compress(json.dumps(metrics).encode('utf-8')),
        headers={'Content-Type': 'application/gzip'}
    )

def test_put_metrics_no_compression(mock_requests_session):
    client = KairosDB('localhost', '8080')
    metrics = [
        {
            'name': 'test.metric',
            'timestamp': 1234567890000,
            'value': 42,
            'tags': {'host': 'test-host'}
        }
    ]
    
    client.put_metrics(metrics, comp=False)
    
    # Verify the POST request was made once with the correct arguments
    mock_requests_session.return_value.post.assert_called_once_with(
        'http://localhost:8080/api/v1/datapoints',
        json.dumps(metrics),
        headers={}
    )

def test_query_metrics(mock_requests_session):
    client = KairosDB('localhost', '8080')
    query = {
        'metrics': [{
            'name': 'test.metric'
        }]
    }
    
    mock_response = mock_requests_session.return_value.post.return_value
    mock_response.json.return_value = {'results': []}
    
    result = client.query_metrics(query)
    
    # Verify the response
    assert result == {'results': []}
    
    # Verify the query was sent correctly
    mock_requests_session.return_value.post.assert_called_once_with(
        'http://localhost:8080/api/v1/datapoints/query',
        data=json.dumps(query),
        headers={'Accept-Encoding': 'gzip, deflate'}
    )

def test_compression(mock_requests_session):
    client = KairosDB('localhost', '8080')
    test_payload = '{"test": "data"}'
    
    # Compress the payload
    compressed = client._compress(test_payload)
    
    # Verify it's compressed correctly by decompressing
    decompressed = gzip.decompress(compressed).decode('utf-8')
    assert decompressed == test_payload 