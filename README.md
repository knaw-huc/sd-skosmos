# SKOSMOS
SKOSMOS container setup

## Run with docker-compose
### Prepare
Create a new repo with a `docker-compose.yml` based on [docker-compose-portainer-template.yml](docker-compose-portainer-template.yml) and a `Dockerfile` based on [Dockerfile-portainer-template](Dockerfile-portainer-template). Replace all instances of `template` appropiately.

Put your vocabularies as `*.ttl` in the `data/` directory accompanied by a `*.config` file. See [countries.ttl.example](./data/countries.ttl.example) and [countries.config.example](./data/countries.config.example) for an example. To try out the example: remove the `.example` suffix.

### To start
```bash
$ docker-compose build
$ docker-compose up -d
```

### To stop:
```bash
$ docker-compose down
```
### Add new vocabularies
Just add the `.ttl` and `.config` to `data/` and restart the containers.

### adapt config.ttl
To overwrite [config-docker-compose.ttl](config-docker-compose.ttl) put also a `config.ttl` in `data/`.

## License
[MIT License](LICENSE.md)
