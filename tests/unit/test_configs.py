import os
import pytest

from monitor.config import parse_config


def test_read_configs(config):
    dbt = 'DISCORD_BOT_TOKEN'

    os.environ[dbt] = config[dbt]

    app_cfg = parse_config('config/default.yaml')

    assert app_cfg['services']['discord']['token'] == config[dbt]


def test_config_not_found(config):
    with pytest.raises(FileNotFoundError) as err:
        app_cfg = parse_config('config/unknown.yaml')

        assert err == FileNotFoundError
