-- CURSOR
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

-- WAYLAND SUPPORT
hl.env("QT_QPA_PLATFORM", "wayland")
hl.env("GDK_BACKEND", "wayland,x11")
hl.env("SDL_VIDEODRIVER", "wayland")
hl.env("CLUTTER_BACKEND", "wayland")

-- ELECTRON APPS
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")

-- THEME
hl.env("GTK_THEME", "Catppuccin-Mocha-Standard-Blue-Dark")

-- MOZILLA
hl.env("MOZ_ENABLE_WAYLAND", "1")

-- DEFAULT APPS
hl.env("BROWSER", "brave")
hl.env("TERMINAL", "kitty")
hl.env("TERMINAL_EXEC", "kitty")
hl.env("FILE_MANAGER", "yazi")
hl.env("EDITOR", "nvim")
hl.env("VISUAL", "nvim")