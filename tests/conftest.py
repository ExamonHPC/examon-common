import pytest
import tempfile
import os

@pytest.fixture
def temp_config_file():
    """Creates a temporary config file for testing"""
    content = """
[MQTT]
MQTT_BROKER = localhost
MQTT_PORT = 1883
MQTT_TOPIC = test/topic

[DAEMON]
TS = 1
PID_FILENAME = /tmp/test.pid
LOG_FILENAME = /tmp/test.log
OUT_PROTOCOL = mqtt
MQTT_FORMAT = csv
COMPRESS = False

[KAIROSDB]
K_SERVERS = localhost
K_PORT = 8080
K_USER = 
K_PASSWORD = 

[LOG]
LOG_LEVEL = DEBUG
LOGFILE_SIZE_B = 5242880
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
        f.write(content)
        config_path = f.name
    
    yield config_path
    
    os.unlink(config_path)

@pytest.fixture
def mock_mqtt_client(mocker):
    """Mocks MQTT client for testing"""
    mock_client = mocker.patch('paho.mqtt.client.Client')
    return mock_client

@pytest.fixture
def mock_requests_session(mocker):
    """Mocks requests Session for KairosDB testing"""
    mock_session = mocker.patch('requests.Session')
    return mock_session 