# API Reference

This document contains the public API reference for census-loader.

## Modules
- census_loader: Main package module exposing Config and utility functions.

## Classes
- Config: Configuration container for API access and request settings. Typical fields include api_key, timeout, and endpoints configuration.

## Functions
- pull_census(config, ...): Fetch data from the Census Bureau API according to the provided Config.
- Additional helper functions may be provided to manage canned queries, caching, and geographies.

## Usage notes
- The exact signatures and behavior should be consulted from the codebase if you need precise details for integration.
