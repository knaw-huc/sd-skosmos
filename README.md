# SKOSMOS
SKOSMOS container setup

## Run with docker-compose
### Prepare
Put your vocabularies as `*.ttl` in the `data/load` directory accompanied by a `*.ttl.config` file. See [countries.ttl.example](./data/load/countries.ttl.example) and [countries.ttl.config.example](./data/load/countries.ttl.config.example) for an example. To try out the example: remove the `.example` suffix.

### To start
```bash
$ docker-compose up -d
```

### To stop:
```bash
$ docker-compose down
```
### Add vocabularies
Just add the `.ttl` and `.ttl.config` to `data/load` and restart the `skosmos-web` container.

## License
[MIT License](LICENSE.md)
