#!/bin/sh
# Now-playing as JSON for eww. Empty line = player gone.
playerctl -F metadata --format '{{status}}	{{artist}}	{{title}}	{{playerName}}' 2>/dev/null |
while IFS='	' read -r s a t p; do
  jq -nc --arg s "$s" --arg a "$a" --arg t "$t" --arg p "$p" '{status:$s,artist:$a,title:$t,player:$p}'
done
