#!/bin/bash
# Toggle Do Not Disturb via swaync / mako
if command -v swaync-client &>/dev/null; then
  swaync-client --toggle-dnd 2>/dev/null
  # Cek status DND setelah toggle
  if swaync-client --get-dnd 2>/dev/null | grep -q "true"; then
    eww update qs_dnd="on"
  else
    eww update qs_dnd="off"
  fi
elif command -v makoctl &>/dev/null; then
  makoctl mode -t dnd 2>/dev/null
  if makoctl mode 2>/dev/null | grep -q "dnd"; then
    eww update qs_dnd="on"
  else
    eww update qs_dnd="off"
  fi
fi
