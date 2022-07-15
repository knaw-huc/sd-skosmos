# skosmos
SKOSMOS container setup

## Run with docker-compose
### Prepare
In the `.env` file, set your sparql backend i.e., `http://fuseki/skosmos/sparql. Then run the following command. 

Put your vocabulary as `*.ttl` in the `data/load` directory accompanied by a `*.ttl.config` file. See [countries.ttl.example](./data/load/countries.ttl.example) and [countries.ttl.config.example](./data/load/countries.ttl.config.example) for an example.

### To start
```bash
$ docker-compose up -d
```

### To stop:
```bash
$ docker-compose down
```

## License

[MIT License](LICENSE.md)
