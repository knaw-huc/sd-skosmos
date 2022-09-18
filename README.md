# SKOSMOS
SKOSMOS container setup

## Run with docker-compose
### Prepare
Put your vocabularies as `*.ttl` in the `data/` directory accompanied by a `*.config` file. See [countries.ttl.example](./data/countries.ttl.example) and [countries.config.example](./data/countries.config.example) for an example. To try out the example: remove the `.example` suffix.

### To start
```bash
$ docker-compose up -d
```

### To stop:
```bash
$ docker-compose down
```
### Add vocabularies
Just add the `.ttl` and `.config` to `data/` and restart the `skosmos-web` container.

### adapt config.ttl
To overwrite [config-docker-compose.ttl](config-docker-compose.ttl) put a config.ttl in `data/`.

## License
[MIT License](LICENSE.md)
