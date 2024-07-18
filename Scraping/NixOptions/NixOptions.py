from elasticsearch import Elasticsearch,RequestsHttpConnection
from base64 import b64encode
import json
import re
import html

class NixScraper:
    def __init__(self, es_host,auth_token):
        self.client = Elasticsearch([es_host],
           headers={"Authorization": f"Basic {auth_token}"},
      
            connection_class=RequestsHttpConnection)
        
    def remove_html_tags(self,text):
       
        clean_text = re.sub(r'<[^>]+>', '', text)
      # Convert HTML entities to characters
        clean_text = html.unescape(clean_text)
        clean_text = clean_text.replace('\n', '')
        return clean_text.strip()
       
    
    def build_query(self, search_term):
        return {
            "from": 0,
            "size": 50,
            "sort": [
                {"_score": "desc", "option_name": "desc"}
            ],
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"type": {"value": "option"}}}
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
                                            "fields": [
                                                "option_name^6",
                                                "option_name.*^3.6",
                                                "option_description^1",
                                                "option_description.*^0.6",
                                                "flake_name^0.5",
                                                "flake_name.*^0.3"
                                            ]
                                        }
                                    },
                                    {
                                        "wildcard": {
                                            "option_name": {
                                                "value": f"*{search_term}*",
                                                "case_insensitive": True
                                            }
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
            "name": hit["_source"]["option_name"],
            "desc": self.remove_html_tags(hit["_source"]["option_description"]),
            "nixName": hit["_source"]["option_source"],
            "type": hit["_source"]["option_type"],
            "value": hit["_source"]["option_default"]
            }
            
            options_list.append(option)
        return options_list

# Now `options_list` contains the list of options with the specified details


# Example usage
if __name__ == "__main__":
    auth_token = "YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g="
    scraper = NixScraper("https://search.nixos.org/backend/",auth_token)
  
    results = scraper.search_options("jupyter")
    print(json.dumps(results))
