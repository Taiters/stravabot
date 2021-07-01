#!/bin/bash

echo "Running cdk diff..."
output=$(cdk diff 2>&1)
exit_code="$?"
echo "$output"

if [ "$exit_code" != "0" ]; then
    echo "cdk diff failed"
    exit 1
fi

diff=$(echo "$output" | awk "/Stack/,/EOF/")
echo "::set-output name=cdk_diff::$diff"
