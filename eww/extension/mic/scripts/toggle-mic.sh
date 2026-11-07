#!/bin/bash
# Toggle mic mixer — auto-close volume mixer
if eww active-windows | grep -q '^mic-mixer:'; then
    eww close mic-mixer
else
    eww close mixer 2>/dev/null
    eww open mic-mixer
fi
