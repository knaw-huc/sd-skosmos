# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Added support for YAML configurations.
- Allow specifying external config/rdf files.
- Added support for trig files.
- Import vocabularies every hour using cron.

## [v2.15-1.1.0]

### Changed

 - Rewrote `entrypoint.sh` as a Python script.
 - Use GraphDB instead of Fuseki.
 - On start, check if vocabularies exist in GraphDB instead of keeping track of local .loaded files.

## [v2.15-1.0.0]

Initial version

[Unreleased]: https://github.com/CLARIAH/skosmos
[v2.15-1.0.0]: https://github.com/CLARIAH/skosmos/releases/tag/v2.15-1.0-RC4
[v2.15-1.1.0]: https://github.com/CLARIAH/skosmos/releases/tag/v2.15-1.1.0
