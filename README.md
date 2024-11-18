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

### adapt config.ttl
To overwrite [config-docker-compose.ttl](config-docker-compose.ttl) put a `config.ttl` in `data/`. To add classifications put them in a `config-ext.ttl` in `data/`.

## Add new vocabularies
In order to add a vocabulary you will need three files. The first one is `{vocabulary-name}.yaml` which needs to be
put in the `data/` directory. The `{vocabulary-name}.config` and `{vocabulary-name}.ttl` files can be in there as well,
but they can also be loaded from an external source. See the example yaml files below to see how to configure them.

### Configuring the vocabulary with `{vocabulary}.yaml`
The yaml file is used for configuring how to load the vocabulary, and whether it needs to be refreshed
at a certain interval. Refreshing is mainly useful when the vocabulary is loaded from an external source.

#### Local Files Example
```yaml
config:
  type: file
  location: my-vocabulary.config

source:
  type: file
  location: my-vocabulary.ttl
```

#### Get Request Example
```yaml
config:
  refresh: Yes
  refreshInterval: 1 # Hours
  type: fetch
  location: https://example.com/path/to/vocabulary.config

source:
  type: fetch
  location: https://example.com/path/to/vocabulary.ttl
  headers:
    X-Custom-Header: Set header values here
```

Note that both config and source support the same configuration options, except `refresh` and `refreshInterval` can only
be set for config (it will affect the entire vocabulary).

#### SPARQL Endpoint Example
You can also load vocabularies from a sparql endpoint. For this, you will need an additional file containing
the sparql query itself, which needs to be in the `data/` directory. For the example, assume we have the query
saved in `data/vocabulary.sparql`.

```yaml
config:
  refresh: Yes
  refreshInterval: 1 # Hours
  type: file
  location: vocabulary.config

source:
  type: sparql
  location: https://example.com/sparql-endpoint
  query_location: vocabulary.sparql
  format: ttl # Used to specify the file extension when it's not clear from the URL what will be returned
```

#### POST request example
You can also retrieve the vocabulary by posting to an endpoint, using a json body.

```yaml
config:
  refresh: Yes
  refreshInterval: 1 # Hours
  type: file
  location: vocabulary.config

source:
  type: post
  location: https://example.com/some-export-endpoint
  format: trig # Used to specify the file extension when it's not clear from the URL what will be returned
  body: {
    "config-a": "some value",
    "config-b": "some other value"
  }
  headers:
    Authorization: Bearer your-token-here
```

## License
[MIT License](LICENSE.md)
