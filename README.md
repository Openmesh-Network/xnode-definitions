# Xnode Definitions
Xnode definitions is a data collection program for data regard

## This definitions pipeline currently has about 15K nix options collected
Total services: 82
Total potential services: 1077

## Project breakdown
service-definitions.json is merely for convenience of viewing the sum of all definitions.
The definitions directory is the actual data desired in the Xnode-Console-Frontend, it is copied into the top-level utils directory.


## To-do
* To get from services to potential services, we can run the nix metadata scraper on a list of these services.
    * Need fields like 'logo', 'name' and 'description' from the package of the same name as the service.
* Manual spec overrides needs to be filled in with data by research.
* Massive cleanup post-refactor is required