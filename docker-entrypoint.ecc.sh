#!/bin/sh
# Writes form endpoints from the environment, then starts the official nginx entrypoint.
# QUOTE_FORM_ENDPOINT is required for delivery. TRADE_FORM_ENDPOINT and
# CAREERS_FORM_ENDPOINT are optional overrides; empty means "use the quote endpoint".
set -eu

js_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

QUOTE=$(js_escape "${QUOTE_FORM_ENDPOINT:-}")
TRADE=$(js_escape "${TRADE_FORM_ENDPOINT:-}")
CAREERS=$(js_escape "${CAREERS_FORM_ENDPOINT:-}")

cat > /usr/share/nginx/html/assets/js/config.js <<EOF
/* Written at container start from QUOTE_FORM_ENDPOINT, TRADE_FORM_ENDPOINT, and CAREERS_FORM_ENDPOINT. */
window.ECC_CONFIG = {
  quoteEndpoint: "${QUOTE}",
  tradeEndpoint: "${TRADE}",
  careersEndpoint: "${CAREERS}"
};
EOF

exec /docker-entrypoint.sh "$@"
