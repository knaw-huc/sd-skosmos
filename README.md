# SKOSMOS
SKOSMOS container setup

## Run with docker-compose
### Prepare
Create a new repo with a `docker-compose.yml` based on [docker-compose-portainer-template.yml](docker-compose-portainer-template.yml) and a `Dockerfile` based on [Dockerfile-portainer-template](Dockerfile-portainer-template). Replace all instances of `template` appropiately.

Put your vocabularies as `*.ttl` in the `data/` directory accompanied by a `*.config` file. See [countries.ttl.example](./data/countries.ttl.example) and [countries.config.example](./data/countries.config.example) for an example. To try out the example: remove the `.example` suffix.

### Containers
This Skosmos setup requires two containers to run (plus additionally a triple store, if that is not hosted externally).

#### sd-skosmos
This is the container responsible for serving the actual Skosmos application. In order for GraphDB support to work this
is based on [our fork of Skosmos](https://github.com/knaw-huc/Skosmos) instead of the plain version. Other than GraphDB
support, this doesn't change anything.

| Env var           | Description                                                                                              |
|-------------------|----------------------------------------------------------------------------------------------------------|
| `SPARQL_ENDPOINT` | The SPARQL endpoint which Skosmos needs to use to connect to the triple store. Only requires read-access |
| `DATA`            | The location of the 'data' folder containing the vocabulary configuration files                          |

#### sd-skosmos-loader
This container is responsible for configuring and importing the used vocabularies based on the configuration files in the `data` directory.
It runs side by side with the Skosmos container and uses cron to run the import script for updating vocabularies from an external source.

| Env var           | Description                                                                                                                                                                                         |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `SPARQL_ENDPOINT` | The SPARQL endpoint which Skosmos needs to use to connect. Should be the same as for the `sd-skosmos` container.                                                                                    |
| `DATABASE_TYPE`   | `graphdb` or `fuseki`                                                                                                                                                                               |
| `STORE_BASE`      | The base endpoint of the triple store. Depends on the type, for GraphDB this is the same as the SPARQL endpoint. For fuseki, include the repository name (e.g. `http://fuseki-domain:3030/skosmos`) |
| `ADMIN_USERNAME`  | The admin username for the triple store (we need write access).                                                                                                                                     |
| `ADMIN_PASSWORD`  | The admin password for the triple store.                                                                                                                                                            |
| `DATA`            | The location of the 'data' folder containing the vocabulary configuration files                                                                                                                     |

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

#### Get Request Example (private GitHub/GitLab repository)
For these get requests, there are two special cases where additional authentication settings can be used. These are
GitHub and GitLab, when you need to access a file in a private repository.

```yaml
# Auth Settings Example
config:
  type: fetch
  location: https://your-gitlab-domain.com/organisation/repository/-/blob/main/vocabulary.config
  auth:
    type: gitlab
    token: your-access-token

source:
  type: fetch
  location: https://raw.githubusercontent.com/organisation/repository/main/vocabulary.trig
  auth:
    type: github
    token: your-access-token
```

The GitLab example will use the file location in the repository to fabricate a call to the GitLab API instead, as
that is the only way to access private repositories. For GitHub, it's just a shortcut for setting the correct headers (make sure
to use the path to the 'raw' file in this case).

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
