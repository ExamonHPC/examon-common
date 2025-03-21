import pytest
from examon.utils.config import Config
import configparser

def test_config_initialization(temp_config_file):
    config = Config(temp_config_file)
    assert config.configfile == temp_config_file

def test_get_defaults(temp_config_file, mocker):
    config = Config(temp_config_file)
    
    # Mock CLI arguments
    mock_args = mocker.patch('argparse.ArgumentParser.parse_args')
    mock_args.return_value = mocker.Mock(
        runmode='run'
    )

    defaults = config.get_conf()
    assert defaults['MQTT_BROKER'] == 'localhost'
    assert defaults['MQTT_PORT'] == '1883'
    assert defaults['OUT_PROTOCOL'] == 'mqtt'

def test_get_conf_with_cli_args(temp_config_file, mocker):
    config = Config(temp_config_file)
    # First parse the config file
    config_parser = configparser.ConfigParser()
    config_parser.read(temp_config_file)
    config.defaults = dict(config_parser['DEFAULT'])
    
    # Mock CLI arguments
    mock_args = mocker.patch('argparse.ArgumentParser.parse_args')
    mock_args.return_value = mocker.Mock(
        MQTT_BROKER='test-broker',
        MQTT_PORT=None,  # Should keep default value
        runmode='run'
    )
    
    conf = config.get_conf()
    assert conf['MQTT_BROKER'] == 'test-broker'
    assert conf['MQTT_PORT'] == '1883'  # Default value preserved 