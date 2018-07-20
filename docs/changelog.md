# Changelog

## 0.6.0

This version inroduces breaking changes to configuration system where we move away from environment-specific config files in favour of .env files and environment variables to lod your sensitive credentials like secret keys, database and 3rd party acces credentials, as outlined in [#77](https://github.com/projectshift/shift-boiler/issues/77) 

This is a breaking change that will require you to update how your app is configured, bootstrapped and run. Please refer to [configuration docs](config.md) for an explanation of how new system operates.


## 0.5.0

This new release updates boiler to use new version of shiftschema (0.2.0) that introduces some breaking changes to validators and filters where previously validation context was being used, now we always get in a model and context is reserved for manually injecting additional validation context.

Because of this, we had to update our validators in user domain. You will need to update your filters and validators code as well when moving to this version.








