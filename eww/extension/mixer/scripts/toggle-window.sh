#!/bin/bash
# Toggle volume mixer — auto-close mic-mixer
if eww active-windows | grep -q '^mixer:'; then
    eww close mixer
else
    eww close mic-mixer 2>/dev/null
    eww open mixer
fi
