#!/usr/bin/env bash
input_file=$1
base_name="${input_file%.*}"
assembly_name="${base_name}.s"
object_name="${base_name}.o"
cat $input_file | bril2json | python compile.py > $assembly_name
as -o $object_name $assembly_name
ld -o $base_name $object_name
