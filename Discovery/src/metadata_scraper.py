from Discovery.src.main import headers
import re
import html
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class NixMetaScraper:
  def __init__(self, es_host):
    self.backend_url = es_host

  def search_metadata(self, search_term):
    query = build_query(search_term)
    channel = "unstable"

    response = requests.post(f'{self.backend_url}/latest-42-nixos-{channel}/_search', headers=headers, json=query)
    response = response.json()    
      
    meta_data = [] 
    for hit in response['hits']['hits']:
      response_data = {
        "name": hit["_source"]["package_attr_name"],
        "desc": self.remove_html_tags(hit["_source"]["package_description"]),
        "website": hit["_source"]["package_homepage"],       
      }      
      meta_data.append(response_data)      
    return meta_data

  def find_metadata(self, services):
    services_with_metadata = []
    for service in services:
      service['meta_data'] = self.search_metadata(service['name'])
      services_with_metadata.append(service)
    return services_with_metadata
  
def build_query(search_term):
  return {
    "from": 0,
    "size": 50,
    "sort": [
      { "_score": "desc" },
      { "package_attr_name": "desc" },
      { "package_pversion": "desc" }
    ],
    "aggs": {
      "package_attr_set": {
        "terms": {
          "field": "package_attr_set",
          "size": 20
        }
      },
      "package_license_set": {
        "terms": {
          "field": "package_license_set",
          "size": 20
        }
      },
      "package_maintainers_set": {
        "terms": {
          "field": "package_maintainers_set",
          "size": 20
        }
      },
      "package_platforms": {
        "terms": {
          "field": "package_platforms",
          "size": 20
        }
      },
      "all": {
        "global": {},
        "aggregations": {
          "package_attr_set": {
            "terms": {
              "field": "package_attr_set",
              "size": 20
            }
          },
          "package_license_set": {
            "terms": {
              "field": "package_license_set",
              "size": 20
            }
          },
          "package_maintainers_set": {
            "terms": {
              "field": "package_maintainers_set",
              "size": 20
            }
          },
          "package_platforms": {
            "terms": {
              "field": "package_platforms",
              "size": 20
            }
          }
        }
      }
    },
    "query": {
      "bool": {
        "filter": [
          { "term": { "type": { "value": "package" } } },
          {
            "bool": {
              "must": [
                { "bool": { "should": [] } },
                { "bool": { "should": [] } },
                { "bool": { "should": [] } },
                { "bool": { "should": [] } }
              ]
            }
          }
        ],
        "must": [
          {
            "dis_max": {
              "tie_breaker": 0.7,
              "queries": [
                {
                  "multi_match": {
                    "type": "cross_fields",
                    "query": search_term,
                    "analyzer": "whitespace",
                    "auto_generate_synonyms_phrase_query": False,
                    "operator": "and",
                    "_name": "multi_match_static-web-server",
                    "fields": [
                      "package_attr_name^9",
                      "package_attr_name.*^5.3999999999999995",
                      "package_programs^9",
                      "package_programs.*^5.3999999999999995",
                      "package_pname^6",
                      "package_pname.*^3.5999999999999996",
                      "package_description^1.3",
                      "package_description.*^0.78",
                      "package_longDescription^1",
                      "package_longDescription.*^0.6",
                      "flake_name^0.5",
                      "flake_name.*^0.3"
                    ]
                  }
                },
                {
                  "wildcard": {
                    "package_attr_name": { "value": f"*{search_term}*", "case_insensitive": True }
                  }
                },
                {
                  "wildcard": {
                    "package_attr_name": {  "value": f"*{search_term}*", "case_insensitive": True }
                  }
                }
              ]
            }
          }
        ]
      }
    }
  }

def extract_favicon_url(url):
    try:
        # Fetch HTML content of the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the favicon link tag
        favicon_tag = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')

        if favicon_tag:
            # Construct absolute URL if the favicon URL is relative
            favicon_url = favicon_tag['href']
            if not favicon_url.startswith('http'):
                favicon_url = urljoin(url, favicon_url)

            return favicon_url
        else:
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None
        

# Now `options_list` contains the list of options with the specified details


# Example usage
if __name__ == "__main__":
    auth_token = "YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g="
    scraper = NixMetaScraper("https://search.nixos.org/backend/",auth_token)
  
    results = scraper.search_options("Ollama")
    for result in results:
        print(result)
