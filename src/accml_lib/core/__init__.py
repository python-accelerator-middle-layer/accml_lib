"""accm\_lib core packages

The `core` contains the modules which
are to be independent of any facility
and form the basis of `àccml\_lib`.

It contains the following main parts:

* models: data models used within the package
* bl: business logic or modules that provide
      basic functionality
* config: configuration data

Interfaces are used to export the interfaces
used within this package.
"""

__all__ = ["model", "config",  "bl",   "interfaces"]