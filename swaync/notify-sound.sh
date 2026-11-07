#!/bin/sh
# swaync script: play a sound for incoming notifications.
# Silent in Do Not Disturb; Discord is skipped because it plays its own sound.
[ "$(swaync-client -D 2>/dev/null)" = "true" ] && exit 0
case "$SWAYNC_APP_NAME" in [Dd]iscord*|vesktop) exit 0 ;; esac
dir=/usr/share/sounds/freedesktop/stereo
case "$SWAYNC_URGENCY" in
  [Cc]ritical) snd=$dir/dialog-warning.oga ;;
  [Ll]ow)      exit 0 ;;                       # low urgency (e.g. volume/progress) stays quiet
  *)           snd=$dir/message.oga ;;
esac
exec pw-play --volume 0.7 "$snd"
