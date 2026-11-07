#!/bin/bash
# Toggle Theme dark/light
current=$(eww get qs_theme 2>/dev/null || echo "dark")
if [ "$current" = "dark" ]; then
  eww update qs_theme="light"
else
  eww update qs_theme="dark"
fi
