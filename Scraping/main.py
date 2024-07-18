import csv
from IconExtractor import extractor
from NixMeta import NixPackageMetaData
from NixOptions import NixOptions
from urllib.parse import urlparse, parse_qs
import json
# Function to read CSV file and extract required columns
def read_csv_and_extract(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get('Name')
            category = row.get('Category')
            link_from_nix_search = row.get('Link from NIX search')
            if name and category and link_from_nix_search:
                data.append({
                    'Name': name,
                    'Category': category,
                    'NixLink': link_from_nix_search
                })
    print("CsvData:", data)
    return data

""" the json format needed is 

[
    {
        "name":"abc"
        "desc":"abc"
        "tags": []
        "logo": "url"
        "specs":{
            "ram": 0
            "storage":0

        }
        "nixName":"abc"
        "options":[
            {
                "name":"abc"
                "desc":"abc"
                "nixName":"abc"
                "type": "abc"
                "value": "val"
            }
        ]
    }
]

what data comes from where ?
name : csv.name
desc : nixmeta
tags : csv.category
logo : IconExtractor
specs : Ideally from csv but unfit csv
nixname : nixmeta
options : nixOptions

data flow 

csv.nixlink -> extract show from query -> pass it to nixpackagemeta and nixOptions -> get homepage from nixmeta -> pass it to IconExtractor
what happens if something fail ? Ignore the package (Not a problem for now)

Simple as that !
"""
filename = 'data/data.csv'  
extracted_data = read_csv_and_extract(filename)

# Metascraper initialization
auth_token = "YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g="
metaScraper = NixPackageMetaData.NixMetaScraper("https://search.nixos.org/backend/",auth_token)

# Optionscraper initialization
optionScraper = NixOptions.NixScraper("https://search.nixos.org/backend/",auth_token)
  

final_json = []
for item in extracted_data:
    # Items are here time to extract the show from url
    parsed_url = urlparse(item['NixLink'])

    # Get the query parameters
    query_params = parse_qs(parsed_url.query)

    # Extract the value of the 'show' parameter
    show_param = query_params.get('show', [''])[0]

    if (show_param):
        Metaresults = metaScraper.search_options(show_param)
        Optionresults = optionScraper.search_options(show_param)
        if(len(Metaresults)>=1):
            if(len(Metaresults[0]['website']) > 0):
                favicon_url = extractor.extract_favicon_url(Metaresults[0]['website'][0])
                print(favicon_url)
                if(favicon_url):
                    pass
                else:
                    favicon_url = ""
            else:
                favicon_url = ""
                Metaresults[0]['website'] = [""]

            final = {
                "name":item["Name"],
                "desc":Metaresults[0]['desc'],
                "tags": [item["Category"]],
                "website":Metaresults[0]["website"][0],
                "implmented":False,
                "logo":favicon_url,
                "specs":{
                     "ram":0,
                      "storage":0
                 },
                 "nixName":show_param,
                 "options":Optionresults
                }

            final_json.append(final)

final_json = json.dumps(final_json, indent=4)
with open('outputs/output.json', 'w') as file:
    # Write a string to the file
    file.write(final_json)
  
                
            
    

