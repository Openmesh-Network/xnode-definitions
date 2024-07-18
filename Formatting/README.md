# Formatting module
This is for any formatting or programatically applied changes to the service definitions where there are problems that can be identified in that manner.

## Data Transformation
We start with raw opensearch response to our query that was defined in `Discovery/src/request_builder.py` and want to work towards the services-definitions format required for the studio.



See the format required by Xnode Admin below, the array inside data["services"] is the format required in the studio. For better readability and version control tracing in git, these array items are all split by file (named according to nixName) in a definitions directory on the frontend.
```
{
    services: [
        {
            nixName: 'service-nix-name'
            options: [
                {
                    nixName: 'service-nix-option-name'
                    type: string
                    value: 'user-defined-choice'
                }, ...
            ]
        }, ...
    ],
    other-modules: [
        ...
    ], ...
}
```
