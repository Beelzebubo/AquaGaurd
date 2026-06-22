#!/usr/bin/env bash
set -euo pipefail

OUT=".output/public"
AS="$OUT/assets"

STYLES=$(ls "$AS"/styles-*.css 2>/dev/null | head -1 | xargs basename)
INDEX=$(ls "$AS"/index-*.js 2>/dev/null | head -1 | xargs basename)
ROUTES=$(ls "$AS"/routes-*.js 2>/dev/null | head -1 | xargs basename)

if [ -z "$STYLES" ] || [ -z "$INDEX" ]; then
  echo "ERROR: built assets not found in $AS"
  ls -la "$AS" 2>/dev/null || echo "  (directory missing)"
  exit 1
fi

cat > "$OUT/index.html" <<EOF
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>AquaGuard — Hydropower Compliance Monitor</title>
<link rel="stylesheet" href="/assets/${STYLES}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet" />
<script async src="https://www.googletagmanager.com/gtag/js?id=G-Q265L4X9YQ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-Q265L4X9YQ');</script>
</head>
<body>
<div id="root"></div>
<script type="module" src="/assets/${INDEX}"></script>
<script type="module" src="/assets/${ROUTES}"></script>
</body>
</html>
EOF
echo "✓ Generated $OUT/index.html"
