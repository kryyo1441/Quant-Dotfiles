-- AUTOSTART
hl.on("hyprland.start", function()
    hl.exec_cmd("waybar")
    hl.exec_cmd("eww daemon")
    hl.exec_cmd("sh -c 'until eww ping >/dev/null 2>&1; do sleep 0.2; done; eww open-many desktop-left desktop-art desktop-right desktop-media'")
    hl.exec_cmd("hyprpaper --config ~/.config/hypr-quant/hyprpaper.conf")

    -- session-wide daemons; skipped in nested test instances (QUANT_NESTED=1)
    if os.getenv("QUANT_NESTED") then return end
    hl.exec_cmd("swaync")
    hl.exec_cmd("nm-applet")
    hl.exec_cmd("blueman-applet")
    hl.exec_cmd("wl-paste --watch cliphist store")
    hl.exec_cmd("/usr/lib/polkit-kde-authentication-agent-1")
    hl.exec_cmd("hypridle")
    hl.exec_cmd("udiskie")
end)
