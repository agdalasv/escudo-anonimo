from __future__ import annotations

DARK: dict[str, str] = {
    "name":         "dark",
    "bg":           "#0d0f11",
    "frame_bg":     "rgba(16, 19, 23, 0.97)",
    "card_bg":      "rgba(24, 28, 34, 0.90)",
    "card_bg_h":    "rgba(30, 35, 42, 0.96)",
    "border":       "rgba(255, 255, 255, 0.07)",
    "border_soft":  "rgba(255, 255, 255, 0.04)",
    "border_hover": "rgba(126, 182, 255, 0.55)",
    "border_active":"rgba(74, 210, 116, 0.70)",
    "border_error": "rgba(239, 103, 103, 0.70)",
    "text":         "#edf0f4",
    "text_muted":   "#8a94a2",
    "text_dim":     "#505a66",
    "green":        "#4ad274",
    "blue":         "#7eb6ff",
    "yellow":       "#e2b15e",
    "red":          "#ef6767",
    "log_fg":       "#c8d0da",
    "log_bg":       "rgba(10, 12, 15, 0.80)",
    "scrollbar":    "rgba(255, 255, 255, 0.10)",
    "input_bg":     "rgba(255, 255, 255, 0.04)",
    "input_border": "rgba(255, 255, 255, 0.08)",
    "tab_active":   "#7eb6ff",
    "title_btn":    "rgba(255, 255, 255, 0.04)",
    "close_hover":  "#ef6767",
    "min_hover":    "#e2b15e",
    "section_bg":   "rgba(255, 255, 255, 0.03)",
}

LIGHT: dict[str, str] = {
    "name":         "light",
    "bg":           "#f0f4f9",
    "frame_bg":     "rgba(246, 249, 255, 0.97)",
    "card_bg":      "rgba(255, 255, 255, 0.88)",
    "card_bg_h":    "rgba(255, 255, 255, 0.99)",
    "border":       "rgba(24, 36, 58, 0.10)",
    "border_soft":  "rgba(24, 36, 58, 0.05)",
    "border_hover": "rgba(0, 85, 238, 0.45)",
    "border_active":"rgba(26, 127, 55, 0.55)",
    "border_error": "rgba(204, 34, 34, 0.55)",
    "text":         "#18243a",
    "text_muted":   "#4c6077",
    "text_dim":     "#8b99aa",
    "green":        "#1a7f37",
    "blue":         "#0055ee",
    "yellow":       "#a05a00",
    "red":          "#cc2222",
    "log_fg":       "#213246",
    "log_bg":       "rgba(255, 255, 255, 0.75)",
    "scrollbar":    "rgba(24, 36, 58, 0.14)",
    "input_bg":     "rgba(255, 255, 255, 0.85)",
    "input_border": "rgba(24, 36, 58, 0.12)",
    "tab_active":   "#0055ee",
    "title_btn":    "rgba(24, 36, 58, 0.04)",
    "close_hover":  "#cc2222",
    "min_hover":    "#a05a00",
    "section_bg":   "rgba(0, 0, 0, 0.02)",
}

_current: dict[str, str] = DARK


def current() -> dict[str, str]:
    return _current


def set_theme(name: str) -> None:
    global _current
    _current = DARK if name == "dark" else LIGHT


def build_qss(c: dict[str, str]) -> str:
    return f"""
* {{
    font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
    font-size: 12px;
    outline: none;
}}

QMainWindow {{
    background-color: {c['bg']};
}}

QWidget#outerBg {{
    background-color: {c['bg']};
}}

QWidget {{
    color: {c['text']};
}}

/* ── app header ── */
QWidget#appHeader {{
    background: transparent;
    border-bottom: 1px solid {c['border_soft']};
}}
QLabel#appTitle {{
    font-size: 13px;
    font-weight: 700;
    color: {c['text']};
    letter-spacing: 4px;
    background: transparent;
}}
QLabel#poweredLbl {{
    font-size: 9px;
    color: {c['text_dim']};
    background: transparent;
    letter-spacing: 1px;
}}
QLabel#logoLbl {{
    background: transparent;
    border: none;
}}
QPushButton#settingsBtn {{
    background: {c['title_btn']};
    border: 1px solid {c['border']};
    border-radius: 13px;
    min-width: 26px; max-width: 26px;
    min-height: 26px; max-height: 26px;
    color: {c['text_dim']};
    font-size: 12px;
    padding: 0;
}}
QPushButton#settingsBtn:hover {{
    border-color: {c['blue']};
    color: {c['blue']};
}}

/* ── status labels ── */
QLabel#statusTitle {{
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 4px;
    background: transparent;
    color: {c['text_muted']};
}}
QLabel#statusSub {{
    font-size: 10px;
    color: {c['text_dim']};
    background: transparent;
    letter-spacing: 1px;
}}

/* ── service cards ── */
QFrame#serviceCard {{
    background-color: {c['card_bg']};
    border: 1px solid {c['border']};
    border-radius: 16px;
}}
QFrame#serviceCard:hover {{
    background-color: {c['card_bg_h']};
    border-color: {c['border_hover']};
}}
QFrame#serviceCard[status="active"] {{
    border-color: {c['border_active']};
    background-color: {c['card_bg_h']};
}}
QFrame#serviceCard[status="connecting"] {{
    border-color: {c['yellow']};
}}
QFrame#serviceCard[status="error"] {{
    border-color: {c['border_error']};
}}
QLabel#cardDesc {{
    font-size: 10px;
    color: {c['text_dim']};
    background: transparent;
}}
QLabel#cardDot {{
    font-size: 7px;
    color: {c['text_dim']};
    background: transparent;
}}
QLabel#cardDot[state="active"]     {{ color: {c['green']};  }}
QLabel#cardDot[state="connecting"] {{ color: {c['yellow']}; }}
QLabel#cardDot[state="error"]      {{ color: {c['red']};    }}
QLabel#cardStatus {{
    font-size: 9px;
    color: {c['text_dim']};
    letter-spacing: 1px;
    background: transparent;
}}
QLabel#cardStatus[state="active"]     {{ color: {c['green']};  }}
QLabel#cardStatus[state="connecting"] {{ color: {c['yellow']}; }}
QLabel#cardStatus[state="error"]      {{ color: {c['red']};    }}
QPushButton#gearBtn {{
    background: {c['section_bg']};
    border: 1px solid {c['border_soft']};
    border-radius: 10px;
    color: {c['text_dim']};
    font-size: 10px;
    padding: 0;
}}
QPushButton#gearBtn:hover {{
    color: {c['text_muted']};
    border-color: {c['border_hover']};
}}

/* ── connect button ── */
QPushButton#connectBtn {{
    background-color: {c['card_bg']};
    border: 1.5px solid {c['border']};
    border-radius: 14px;
    font-size: 11px;
    font-weight: 700;
    color: {c['text_muted']};
    letter-spacing: 7px;
    min-height: 50px;
}}
QPushButton#connectBtn:hover:!checked {{
    border-color: {c['blue']};
    color: {c['blue']};
    background-color: {c['card_bg_h']};
}}
QPushButton#connectBtn:checked {{
    border: 1.5px solid {c['green']};
    color: {c['green']};
    background-color: {c['card_bg']};
}}
QPushButton#connectBtn:disabled {{
    background-color: {c['frame_bg']};
    border-color: {c['border']};
    color: {c['text_dim']};
}}

/* ── log ── */
QTextEdit#log {{
    background-color: {c['log_bg']};
    border: 1px solid {c['border']};
    border-radius: 12px;
    color: {c['log_fg']};
    font-size: 10px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    padding: 8px 10px;
    selection-background-color: {c['blue']};
}}

/* ── settings panel ── */
QFrame#settingsCard {{
    background-color: {c['frame_bg']};
    border: 1px solid {c['border']};
    border-radius: 18px;
}}
QLabel#panelTitle {{
    font-size: 12px;
    font-weight: 700;
    color: {c['text']};
    letter-spacing: 4px;
}}
QLabel#settingSection {{
    font-size: 8px;
    color: {c['text_dim']};
    letter-spacing: 3px;
    font-weight: 700;
}}
QLabel#settingLabel {{
    font-size: 11px;
    color: {c['text_muted']};
}}
QPushButton#saveBtn {{
    background-color: {c['green']};
    border: none;
    border-radius: 10px;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    min-height: 36px;
    padding: 0 20px;
}}
QPushButton#saveBtn:hover {{ opacity: 0.85; }}
QPushButton#closeBtn {{
    background: transparent;
    border: 1px solid {c['border']};
    border-radius: 10px;
    color: {c['text_muted']};
    font-size: 11px;
    min-height: 36px;
    padding: 0 16px;
}}
QPushButton#closeBtn:hover {{
    border-color: {c['red']};
    color: {c['red']};
}}

/* ── inputs ── */
QSpinBox, QLineEdit {{
    background-color: {c['input_bg']};
    border: 1px solid {c['input_border']};
    border-radius: 9px;
    color: {c['text']};
    padding: 5px 10px;
    min-height: 28px;
    selection-background-color: {c['blue']};
}}
QSpinBox:focus, QLineEdit:focus {{ border-color: {c['blue']}; }}
QSpinBox::up-button, QSpinBox::down-button {{
    background: transparent; border: none; width: 16px;
}}
QLineEdit#btcInput {{
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 10px;
    color: {c['text_muted']};
}}
QPushButton#copyBtn {{
    background: {c['section_bg']};
    border: 1px solid {c['border_soft']};
    border-radius: 8px;
    color: {c['text_dim']};
    font-size: 12px;
    padding: 0;
}}
QPushButton#copyBtn:hover {{
    background: {c['blue']};
    color: #ffffff;
    border-color: {c['blue']};
}}

/* ── blocker ── */
QLineEdit#sitesInput {{
    background-color: {c['input_bg']};
    border: 1px solid {c['input_border']};
    border-radius: 9px;
    color: {c['text']};
    padding: 5px 10px;
    min-height: 28px;
}}
QPushButton#addSiteBtn {{
    background: {c['section_bg']};
    border: 1px solid {c['border_soft']};
    border-radius: 8px;
    color: {c['text_muted']};
    font-size: 11px;
    padding: 6px 12px;
}}
QPushButton#addSiteBtn:hover {{
    border-color: {c['blue']};
    color: {c['blue']};
}}
QTextEdit#sitesList {{
    background-color: {c['input_bg']};
    border: 1px solid {c['input_border']};
    border-radius: 9px;
    color: {c['text_dim']};
    font-size: 10px;
    padding: 8px;
}}
QPushButton#showPassBtn {{
    background: {c['section_bg']};
    border: 1px solid {c['border_soft']};
    border-radius: 8px;
    color: {c['text_dim']};
    font-size: 11px;
}}
QPushButton#showPassBtn:hover {{
    border-color: {c['blue']};
}}

/* ── tabs ── */
QTabWidget::pane {{
    border: 1px solid {c['border']};
    border-radius: 12px;
    background-color: {c['card_bg']};
    top: -1px;
}}
QTabBar::tab {{
    background: transparent;
    color: {c['text_dim']};
    padding: 7px 14px;
    border: none;
    font-size: 9px;
    letter-spacing: 2px;
    font-weight: 700;
}}
QTabBar::tab:selected {{
    color: {c['text']};
    border-bottom: 2px solid {c['tab_active']};
}}
QTabBar::tab:hover:!selected {{ color: {c['text_muted']}; }}

/* ── scrollbars ── */
QScrollBar:vertical {{
    background: transparent; width: 4px; border: none; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c['scrollbar']}; border-radius: 2px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent; height: 4px; border: none;
}}
QScrollBar::handle:horizontal {{
    background: {c['scrollbar']}; border-radius: 2px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
"""
