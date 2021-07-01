#!/bin/bash

echo "Running cdk diff..."
output=$(cdk diff 2>&1)
if [ "$?" == "0" ]
then
    result="Success"
else
    result="Failure"
fi

echo "$output"

diff=$(echo "$output" | awk "/Stack/,/EOF/")
comment="\`cdk diff\` - $result
<details><summary>diff</summary>
\`\`\`
${diff}
\`\`\`
</details>
"
payload=$(echo "${comment}" | jq -R --slurp '{body: .}')
comments_url=$(cat ${GITHUB_EVENT_PATH} | jq -r .pull_request.comments_url)

echo "${payload}" | curl -s -S -H "Authorization: token ${GITHUB_TOKEN}" \
    --header "Content-Type: application/json" \
    --data @- "${comments_url}" > /dev/null