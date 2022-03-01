# Multisigs Monitor 📡📄
Configurable events monitor of https://gnosis-safe.io/ contracts with discord bot as `notifier`.
Notifier can be easly replaced or new ones added to `_publish` your events.

Was initially built to complite https://github.com/Badger-Finance/gitcoin/issues/44 bounty.

## Development 🛠
This project is using `Lets` CLI task manager with docker under the hood, follow link to install
https://lets-cli.org/docs/installation/.

### Configuration 🗃
Follow bot setup flow accoding to https://discordpy.readthedocs.io/en/latest/index.html#getting-started.

`CONFIG_PATH` env var points to current config used in app. 

List of channels ids, that will receive notifications
```yaml
subscribers:
  - 943420446773248010
```

Map of networks and contract, that u want to observe
```yaml
networks:
    mainnet:
      - label: dev
        addr: '0xB65cef03b9B89f99517643226d76e286ee999e77'
```

> For now notification interval is hardcoded to 5 min. Feel free to change the value in
> `_collect_interval`

### Lets CLI 🖤
Init `venv` for python, and install all backend deps
```shell
lets init
```

It`s preferable to enable **git hooks**. It will launch flake8,
on pre-commit stage, to keep ur code clean ;)
```shell
lets enable-hooks
```

Specify bot token. It will save it to a file,
the value of wich will be taken to the ENV var by `lets`, when the app starts
```shell
lets add-bot-token <token>
```

If u want to interact with project modules
```shell
lets ishell
```

Run monitor service with discord bot
```shell
lets run
```
You can find more command in `lets.yaml` or just typing `lets` in terminal.

## Deploy 🚀
Monitor is build by docker, all u need is fill set of `env` vars:
- `CONFIG_PATH`
- `DISCORD_BOT_TOKEN`

And launch your image on desired platform.
