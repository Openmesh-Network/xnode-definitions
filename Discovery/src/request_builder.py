def build_packages_request(search_term=None, **kwargs) -> dict:
    if kwargs.get("package") is not None:
        package = kwargs.get("package")
    elif search_term is not None:
        package = search_term
    package_set_filter = []
    package_set_value = kwargs.get("package_set")
    if package_set_value:
        package_set_filter.append({
            "term":{
                "package_attr_set": {
                    "_name": "filter_bucket_package_attr_set",
                    "value": package_set_value
                },
            }
        })

    license_filter = []
    license_value = kwargs.get("license")
    if license_value:
        license_filter.append({
            "term": {
                "package_license_set": {
                    "_name": "filter_bucket_package_license_set",
                    "value": license_value
                }
            }
        })

    maintainer_filter = []
    maintainer_value = kwargs.get("maintainer")
    if maintainer_value:
        maintainer_filter.append({
            "term": {
                "package_maintainers_set": {
                    "_name": "filter_bucket_package_maintainers_set",
                    "value": maintainer_value
                }
            }
        })

    platform_filter = []
    platform_value = kwargs.get("platform")
    if platform_value:
        platform_filter.append({
            "term": {
                "package_platforms": {
                    "_name": "filter_bucket_package_platforms",
                    "value": platform_value
                }
            }
        })

    package_request_data = {
        "from": kwargs.get("begin"),
        "size": kwargs.get("size"),
        "query": {
            "bool": {
                "filter": [
                    {"term": {"type": {"value": "package", "_name": "filter_packages"}}},
                    {"bool": {"must": [
                        {"bool": {"should": package_set_filter}},
                        {"bool": {"should": license_filter}},
                        {"bool": {"should": maintainer_filter}},
                        {"bool": {"should": platform_filter}}
                    ]}}
                ],
                "must": [
                    {"dis_max": {
                        "queries": [
                            {"multi_match": {
                                "query": package,
                                "fields": [
                                    "package_attr_name^9",
                                    "package_pname^6",
                                    "package_description^1.3"
                                ]
                            }},
                            {
                                "wildcard": {
                                    "package_attr_name": {
                                        "value": f"*{kwargs.get('package')}*",
                                        "case_insensitive": True
                                    }
                                }
                            }
                        ]
                    }}
                ]
            }
        }
    }
    return package_request_data

def build_options_request(**kwargs) -> dict:
    option_set_filter = []
    option_set_value = kwargs.get("option_set")
    if option_set_value:
        option_set_filter.append({
            "term":{
                "package_attr_set": {
                    "_name": "filter_bucket_package_attr_set",
                    "value": option_set_value
                },
            }
        })

    license_filter = []
    license_value = kwargs.get("license")
    if license_value:
        license_filter.append({
            "term": {
                "package_license_set": {
                    "_name": "filter_bucket_package_license_set",
                    "value": license_value
                }
            }
        })

    maintainer_filter = []
    maintainer_value = kwargs.get("maintainer")
    if maintainer_value:
        maintainer_filter.append({
            "term": {
                "package_maintainers_set": {
                    "_name": "filter_bucket_package_maintainers_set",
                    "value": maintainer_value
                }
            }
        })

    platform_filter = []
    platform_value = kwargs.get("platform")
    if platform_value:
        platform_filter.append({
            "term": {
                "package_platforms": {
                    "_name": "filter_bucket_package_platforms",
                    "value": platform_value
                }
            }
        })

    option_request_data = {
        "from": kwargs.get("begin"),
        "size": kwargs.get("size"),
        "query": {
            "bool": {
                "filter": [
                    {"term": 
                        {"type": {"value": "option"},
                    }},
                    
                    {"bool": {"must": [
                        {"bool": {"should": option_set_filter}},
                        {"bool": {"should": license_filter}},
                        {"bool": {"should": maintainer_filter}},
                        {"bool": {"should": platform_filter}}
                    ]}}
                ],
                "must": [
                    {"dis_max": {
                        "tie_breaker": 0.7,
                        "queries": [
                            {"match": {
                                "option_name":{
                                    "query": kwargs.get("package")
                                }  
                            }},
                            {
                                "wildcard": {
                                    "option_name": {
                                        "value": f"*{kwargs.get('package')}*",
                                        "case_insensitive": True
                                    }
                                }
                            }
                        ]
                    }}
                ]
            }
        }
    }
    return option_request_data