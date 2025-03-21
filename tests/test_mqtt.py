import pytest
from examon.transport.mqtt import Mqtt
import json

def test_mqtt_initialization(mock_mqtt_client):
    mqtt = Mqtt('localhost', '1883', username='user', password='pass')
    assert mqtt.brokerip == 'localhost'
    assert mqtt.brokerport == '1883'
    assert mqtt.status == 1

def test_put_metrics_csv(mock_mqtt_client):
    mqtt = Mqtt('localhost', '1883', format='csv')
    metrics = [{
        'name': 'test.metric',
        'timestamp': 1234567890000,
        'value': 42,
        'tags': {'host': 'test-host'}
    }]
    
    mqtt.put_metrics(metrics)

    mock_mqtt_client.return_value.publish.assert_called_once_with(
        'host/test-host/test.metric',
        payload='42;1234567890.000', 
        qos=0, 
        retain=False
    )

def test_put_metrics_json(mock_mqtt_client):
    mqtt = Mqtt('localhost', '1883', format='json', outtopic='test/topic')
    metrics = [{
        'name': 'test.metric',
        'timestamp': 1234567890000,
        'value': 42,
        'tags': {'host': 'test-host'}
    }]
    
    mqtt.put_metrics(metrics)

    mock_mqtt_client.return_value.publish.assert_called_once_with(
        'test/topic',
        payload=json.dumps(metrics[0]),
        qos=0,
        retain=False
    ) 