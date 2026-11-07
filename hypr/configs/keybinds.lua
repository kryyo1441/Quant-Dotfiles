-- KEYBINDS
local mainMod = "SUPER"

-- APPLICATIONS
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("kitty"))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd("rofi -show drun -theme ~/dotfiles/Quant-Dotfiles/rofi/config.rasi"))
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd("~/.config/hypr-quant/bin/quant-handoff"))
hl.bind(mainMod .. " + A", hl.dsp.exec_cmd("~/dotfiles/Quant-Dotfiles/eww/extension/quick-settings/scripts/toggle-window.sh"))
hl.bind(mainMod .. " + Z", hl.dsp.exec_cmd("kitty"))
hl.bind(mainMod .. " + X", hl.dsp.exec_cmd("thunar"))
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd("code"))
hl.bind(mainMod .. " + SHIFT + V", hl.dsp.exec_cmd("kitty -e nvim"))
hl.bind(mainMod .. " + V", hl.dsp.exec_cmd("cliphist list | rofi -dmenu | cliphist decode | wl-copy"))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("brave"))
hl.bind(mainMod .. " + space", hl.dsp.exec_cmd("rofi -show drun -theme ~/dotfiles/Quant-Dotfiles/rofi/config.rasi"))
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("brave --profile-directory=Default --app-id=hnpfjngllnobngcgfapefoaidbinmjnm"))  -- WhatsApp Web PWA
hl.bind(mainMod .. " + S", hl.dsp.exec_cmd("kitty sh -c 'spotatui; exec bash'"))  -- shell stays after spotatui quits
hl.bind(mainMod .. " + ALT + W", hl.dsp.exec_cmd("~/dotfiles/Quant-Dotfiles/rofi/scripts/wallpaper-select.sh"))

-- PANEL CONTROL
hl.bind("SUPER + Menu", hl.dsp.exec_cmd("~/dotfiles/Quant-Dotfiles/eww/extension/quick-settings/scripts/toggle-swaync.sh"))
hl.bind("CTRL + Menu", hl.dsp.exec_cmd("~/dotfiles/Quant-Dotfiles/eww/extension/quick-settings/scripts/toggle-window.sh"))
hl.bind(mainMod .. " + SHIFT + W", hl.dsp.exec_cmd("~/dotfiles/Quant-Dotfiles/waybar/scripts/reload.sh"))

-- WINDOW CONTROL
hl.bind(mainMod .. " + Q", hl.dsp.window.close())
hl.bind(mainMod .. " + BackSpace", hl.dsp.window.close())
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + SHIFT + T", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + SHIFT + J", hl.dsp.layout("togglesplit"))

-- MOVE FOCUS
hl.bind(mainMod .. " + left", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down", hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + L", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + K", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + J", hl.dsp.focus({ direction = "down" }))

-- MOVE WINDOWS
hl.bind(mainMod .. " + SHIFT + left", hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + up", hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + down", hl.dsp.window.move({ direction = "down" }))

-- RESIZE WINDOWS
hl.bind(mainMod .. " + CTRL + right", hl.dsp.window.resize({ x = 50, y = 0, relative = true }), { repeating = true })
hl.bind(mainMod .. " + CTRL + left", hl.dsp.window.resize({ x = -50, y = 0, relative = true }), { repeating = true })
hl.bind(mainMod .. " + CTRL + up", hl.dsp.window.resize({ x = 0, y = -50, relative = true }), { repeating = true })
hl.bind(mainMod .. " + CTRL + down", hl.dsp.window.resize({ x = 0, y = 50, relative = true }), { repeating = true })

-- WORKSPACES
for workspace = 1, 10 do
    local key = workspace % 10
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = workspace }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = workspace, follow = false }))
end

-- MOUSE CONTROL
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- MEDIA CONTROL
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"), { repeating = true, locked = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { repeating = true, locked = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
hl.bind(mainMod .. " + F3", hl.dsp.exec_cmd("sh -c 'eww active-windows | grep -q \"^mixer:\" && eww close mixer || (eww close mic-mixer; eww open mixer)'"))
hl.bind(mainMod .. " + F4", hl.dsp.exec_cmd("sh -c 'eww active-windows | grep -q \"^mic-mixer:\" && eww close mic-mixer || (eww close mixer; eww open mic-mixer)'"))
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl set +10%"), { repeating = true, locked = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl set 10%-"), { repeating = true, locked = true })

-- SCREENSHOT
hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd("grim - | wl-copy"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("grim -g \"$(slurp)\" - | wl-copy"))

-- SESSION CONTROL
hl.bind(mainMod .. " + ALT + F10", hl.dsp.exit())
hl.bind(mainMod .. " + ALT + F11", hl.dsp.exec_cmd("systemctl reboot"))
hl.bind(mainMod .. " + ALT + F12", hl.dsp.exec_cmd("systemctl poweroff"))
hl.bind(mainMod .. " + ALT + F8", hl.dsp.exec_cmd("systemctl hibernate"))
hl.bind(mainMod .. " + ALT + F9", hl.dsp.exec_cmd("systemctl suspend"))

-- RELOAD CONFIG
hl.bind(mainMod .. " + SHIFT + R", hl.dsp.exec_cmd("hyprctl reload"))

-- LOCKSCREEN
hl.bind(mainMod .. " + CTRL + L", hl.dsp.exec_cmd("hyprlock"))