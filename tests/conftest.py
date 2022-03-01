import pytest


@pytest.fixture()
def config():
    print('Working just fine')

    return {
        'DISCORD_BOT_TOKEN': 'test'
    }
