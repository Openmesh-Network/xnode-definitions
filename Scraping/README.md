Run all programs from the top directory. There are 3 functions that can be used, none will generate different output without change to the inputs (or an update of the scraped resources).

1. Scrape nix services and options using csv data (awesome self-hosted + nix)

`python main.py`

2. Option enumeration to find all the types of options there are.

`python utils/optionEnumeration.py`

3. Create a properly formatted service-definition and combined it with manually curated definitions.
    * Used to define all valid configurable options on the Xnode Studio.

`python utils/config_wrangler.py`

### To-do
* Add support for options which are related to but not childs of the service, such as prometheus exporters and ssh authorizedKeys.