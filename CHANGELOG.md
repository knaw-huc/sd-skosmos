# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

 - Rewrote `entrypoint.sh` as a Python script
 - Use GraphDB instead of Fuseki
 - On start, check if vocabularies exist in GraphDB instead of keeping track of local .loaded files.
