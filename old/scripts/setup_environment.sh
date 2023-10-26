#!/bin/bash
environment=$(aws lambda list-functions \
    | jq '.Functions[] | select(.FunctionName | contains("ApiHandler")).Environment.Variables | to_entries | map(.key + "=" + .value)[]' -r)


while read -r line; do
    echo "$line"
    export $line
done <<< $environment
