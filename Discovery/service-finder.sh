#!/bin/bash

# Loop through each lowercase letter of the alphabet
for letter in {a..z}
do
  # Construct the output filename
  output_file="${letter}.json"
  
  # Call the Python program with the current letter and output file
  python src/main.py --channel unstable --options --size 10000 "services.${letter}" --output "data/services/${output_file}"
done
