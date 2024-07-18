from elasticsearch import Elasticsearch, RequestsHttpConnection
from base64 import b64encode
import json
import re
import html

class NixMetaScraper:
    def __init__(self, es_host,auth_token):
        self.client = Elasticsearch([es_host],
           headers={"Authorization": f"Basic {auth_token}"},
      
            connection_class=RequestsHttpConnection)
        
    def remove_html_tags(self,text):
        
        if (text):
          clean_text = re.sub(r'<[^>]+>', '', text)
      # Convert HTML entities to characters
          clean_text = html.unescape(clean_text)
          clean_text = clean_text.replace('\n', '')
          return clean_text.strip()
        return ""
    
    def build_query(self, search_term):
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

    def search_options(self, search_term):
        query = self.build_query(search_term)
        response = self.client.search(index="latest-42-nixos-24.05", body=query)
        options_list = []
        
        for hit in response['hits']['hits']:
            option = {
            "name": hit["_source"]["package_attr_name"],
            "desc": self.remove_html_tags(hit["_source"]["package_description"]),
            "website": hit["_source"]["package_homepage"],
          
            }
            
            options_list.append(option)
        return options_list

# Now `options_list` contains the list of options with the specified details


# Example usage
if __name__ == "__main__":
    auth_token = "YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g="
    scraper = NixMetaScraper("https://search.nixos.org/backend/",auth_token)
  
    results = scraper.search_options("Ollama")
    for result in results:
        print(result)
