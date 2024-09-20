#!/bin/bash

for file in ../../bril/benchmarks/mem/*.bril; do
    # echo "Processing $file"
    # Run the command for each file
    pre_lc=$(cat "$file" | wc -l)
    opt_lc=$(cat "$file" | bril2json | python3 gdce.py | bril2txt | wc -l)
    echo "$file,$pre_lc,$opt_lc"
done
