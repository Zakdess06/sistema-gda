# app/utils/button_styles.py
"""Estilos reutilizables para botones en Windows 10"""

PRIMARY_BUTTON_STYLE = """
    QPushButton {
        min-height: 40px;
        min-width: 100px;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        background-color: #2563eb;
        color: white;
        border: none;
    }
    QPushButton:hover {
        background-color: #3b82f6;
    }
    QPushButton:pressed {
        background-color: #1e40af;
    }
"""

ACTION_BUTTON_STYLE = """
    QPushButton {
        min-height: 40px;
        min-width: 100px;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        background-color: #161d26;
        color: #f0f4f8;
        border: 1px solid #1f2937;
    }
    QPushButton:hover {
        background-color: #1f2937;
        border-color: #9ca3af;
    }
    QPushButton:pressed {
        background-color: #0f1419;
    }
"""

DANGER_BUTTON_STYLE = """
    QPushButton {
        min-height: 40px;
        min-width: 100px;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        background-color: #dc2626;
        color: white;
        border: none;
    }
    QPushButton:hover {
        background-color: #ef4444;
    }
    QPushButton:pressed {
        background-color: #991b1b;
    }
"""

def apply_button_style(button, style_type):
    """Aplica estilo a un botón según su tipo"""
    button.setMinimumHeight(40)
    if style_type == "primary":
        button.setStyleSheet(PRIMARY_BUTTON_STYLE)
    elif style_type == "action":
        button.setStyleSheet(ACTION_BUTTON_STYLE)
    elif style_type == "danger":
        button.setStyleSheet(DANGER_BUTTON_STYLE)
