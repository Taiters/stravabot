#!/bin/bash

ENDPOINT="https://www.strava.com/api/v3/push_subscriptions"

create_webhook() {
    url="$1"
    token="$2"
    echo "Creating webhook.."
    echo "Callback URL: $url"
    echo "Verify token: $token"
    echo ""

    curl -s -X POST "$ENDPOINT" \
        -F client_id="$STRAVA_CLIENT_ID" \
        -F client_secret="$STRAVA_CLIENT_SECRET" \
        -F callback_url="$url" \
        -F verify_token="$token" | jq
}

get_webhook() {
    curl -s -G "$ENDPOINT" \
        -d client_id="$STRAVA_CLIENT_ID" \
        -d client_secret="$STRAVA_CLIENT_SECRET" | jq
}

delete_webhook() {
    id="$1"
    echo "Deleting webhook $id..."
    curl -s -X DELETE "$ENDPOINT/$id" \
        -F client_id="$STRAVA_CLIENT_ID" \
        -F client_secret="$STRAVA_CLIENT_SECRET" | jq
}

test_webhook() {
    url="$1"
    owner_id=$2
    activity_id=$3

    curl -X POST "$url" -H "Content-Type: application/json" \
        -d "{\"dry_run\":true,\"aspect_type\":\"create\",\"event_time\":11111111,\"object_id\":$activity_id,\"object_type\":\"activity\",\"owner_id\":$owner_id,\"subscription_id\":999999}"
}

command="$1"
if [ "$command" == "create" ]; then
    create_webhook "$2" "$3"
elif [ "$command" == "get" ]; then
    get_webhook
elif [ "$command" == "delete" ]; then
    delete_webhook "$2"
elif [ "$command" == "test" ]; then
    test_webhook "$2" $3 $4
else
    echo "Commands: create, get, delete, test"
fi