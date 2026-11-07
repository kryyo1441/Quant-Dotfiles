#!/bin/sh
# Bars for the desktop visualizer. cava's sleep_timer idles it when there's no audio.
stdbuf -oL cava -p "$(dirname "$0")/../cava.conf" 2>/dev/null | sed -u 's/;//g;y/01234567/▁▂▃▄▅▆▇█/'
