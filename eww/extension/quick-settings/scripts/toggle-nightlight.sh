#!/bin/bash
# Cycle Night Light: off → 25% → 50% → 75% → 100% → off (loop)
# Level = seberapa hangat layar (makin tinggi makin warm / Kelvin makin rendah)
# State di /tmp biar konsisten antar klik & survive eww reload
STATE="/tmp/qs_nightlight.state"

# mapping level → temperatur Kelvin
temp_for() {
  case "$1" in
    25%)  echo 5500 ;;
    50%)  echo 4500 ;;
    75%)  echo 3900 ;;
    100%) echo 3400 ;;
  esac
}

cur=$(cat "$STATE" 2>/dev/null || echo "off")
# guard desync: state bilang nyala tapi proses mati → anggap off
pgrep -x hyprsunset >/dev/null 2>&1 || cur="off"

case "$cur" in
  off)  next="25%" ;;
  25%)  next="50%" ;;
  50%)  next="75%" ;;
  75%)  next="100%" ;;
  *)    next="off" ;;
esac

if [ "$next" = "off" ]; then
  pkill -x hyprsunset 2>/dev/null
elif pgrep -x hyprsunset >/dev/null 2>&1; then
  # instance sudah jalan → ganti temperatur via IPC, tanpa flicker
  hyprctl hyprsunset temperature "$(temp_for "$next")" >/dev/null 2>&1
else
  # stdout/stderr dibuang — biar gak mati SIGPIPE kalau parent pipe tutup
  hyprsunset -t "$(temp_for "$next")" >/dev/null 2>&1 &
fi

echo "$next" > "$STATE"
eww update qs_nightlight="$next" 2>/dev/null
