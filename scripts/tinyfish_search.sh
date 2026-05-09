#!/bin/bash
# TinyFish Search CLI Wrapper
# Usage: ./tinyfish_search.sh "search query" [location] [language] [page]
#   or:  ./tinyfish_search.sh --fetch <url1> [url2 ...]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$HOME/.hermes/.env"

# Load API key from .env
if [ -f "$ENV_FILE" ]; then
    export $(grep -E '^TINYFISH_API_KEY=' "$ENV_FILE" 2>/dev/null || true)
fi

API_KEY="${TINYFISH_API_KEY:-}"

if [ -z "$API_KEY" ]; then
    echo "❌ TINYFISH_API_KEY not set. Add to ~/.hermes/.env or export it."
    exit 1
fi

if [ "$1" = "--fetch" ]; then
    # Fetch mode
    shift
    if [ $# -eq 0 ]; then
        echo "❌ Usage: $0 --fetch <url1> [url2 ...]"
        exit 1
    fi
    # Build JSON payload
    URLs=$(python3 -c "import json; print(json.dumps($(printf '%s\n' "$@" | python3 -c "import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" 2>/dev/null || echo '["$@"]')))")
    
    curl -s --max-time 120 -X POST "https://api.fetch.tinyfish.ai" \
      -H "X-API-Key: $API_KEY" \
      -H "Content-Type: application/json" \
      -d "$(python3 -c "
import json, sys
urls = sys.argv[1:]
print(json.dumps({'urls': urls, 'format': 'markdown'}))
" "$@")" 2>/dev/null | python3 -m json.tool 2>/dev/null || {
        # Fallback raw output
        curl -s --max-time 120 -X POST "https://api.fetch.tinyfish.ai" \
          -H "X-API-Key: $API_KEY" \
          -H "Content-Type: application/json" \
          -d "$(python3 -c "
import json, sys
urls = sys.argv[1:]
print(json.dumps({'urls': urls, 'format': 'markdown'}))
" "$@")"
    }
else
    # Search mode
    QUERY="${1:-}"
    LOCATION="${2:-US}"
    LANGUAGE="${3:-en}"
    PAGE="${4:-0}"
    
    if [ -z "$QUERY" ]; then
        echo "❌ Usage: $0 \"search query\" [location] [language] [page]"
        echo "   or:  $0 --fetch <url1> [url2 ...]"
        exit 1
    fi
    
    # URL-encode the query
    ENCODED_QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")
    
    curl -s --max-time 15 "https://api.search.tinyfish.ai?query=${ENCODED_QUERY}&location=${LOCATION}&language=${LANGUAGE}&page=${PAGE}" \
      -H "X-API-Key: $API_KEY" 2>/dev/null | python3 -m json.tool 2>/dev/null || {
        # Fallback raw output
        curl -s --max-time 15 "https://api.search.tinyfish.ai?query=${ENCODED_QUERY}&location=${LOCATION}&language=${LANGUAGE}&page=${PAGE}" \
          -H "X-API-Key: $API_KEY"
    }
fi
