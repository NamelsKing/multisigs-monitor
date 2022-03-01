import os
import re

from typing import Optional

import trafaret as t

from trafaret_config import parse_and_validate

from monitor.types import Config

config: Optional[Config] = None

MULTISIG_TRAFARET = t.Dict({
    'networks': t.Mapping(
        t.String(),
        t.List(
            t.Dict({
                'label': t.String(),
                'addr': t.String(),
            })
        )
    )
})

SERVICES_TRAFARET = t.Dict({
    'discord': t.Dict({
        'token': t.String(),
        'subscribers': t.List(t.Int())
    }),
    'gnosis': t.Dict({
        'url': t.String()
    })
})

CONFIG_TRAFARET = t.Dict({
    'services': SERVICES_TRAFARET,
    'multisig': MULTISIG_TRAFARET
})


ENV_RE = re.compile(r'{{(.+?)}}')


def replace_env(raw_config: str, env: dict[str, str]) -> str:
    """Replaces {{STRING}} entries in raw yaml"""
    keys = ENV_RE.findall(raw_config)
    for key in keys:
        if key not in env:
            raise RuntimeError(
                f'{key} specified in config but not specified in env'
            )

        pattern = r'{{%s}}' % key  # noqa: S001
        value = str(env[key])
        raw_config = re.sub(pattern, value, raw_config)

    return raw_config


def parse_config(file_path: str) -> Config:
    global config
    with open(file_path) as f:
        raw_config = f.read()
        raw_config = replace_env(raw_config, dict(os.environ))

    config = parse_and_validate(raw_config, CONFIG_TRAFARET)
    if config is None:
        raise RuntimeError(f'Config not found: {config}')

    return config


def get_config_path() -> str:
    config_path = os.environ.get('CONFIG_PATH')
    if not config_path:
        raise ValueError('CONFIG_PATH must be specified')

    return config_path


def get_config() -> Config:
    if config:
        return config

    config_path = get_config_path()
    return parse_config(config_path)
