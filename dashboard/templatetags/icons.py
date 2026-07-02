from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Same outline icon set (stroke-based, ~1.75px) as the React app's
# src/components/icons.jsx, ported to inline SVG for server-rendered templates.
_ICON_PATHS = {
    "home": (
        '<path d="M3.5 10.5 12 3.5l8.5 7" />'
        '<path d="M5.5 9.5V19a1 1 0 0 0 1 1h3.5v-5.8h4V20H17.5a1 1 0 0 0 1-1V9.5" />'
    ),
    "users": (
        '<circle cx="9" cy="8.2" r="3" />'
        '<path d="M3.8 20c0-2.9 2.3-5.2 5.2-5.2s5.2 2.3 5.2 5.2" />'
        '<circle cx="17" cy="9" r="2.3" />'
        '<path d="M15.3 20c.2-2.2 1.8-3.9 3.7-4.3" />'
    ),
    "clipboard": (
        '<rect x="5.5" y="4.5" width="13" height="16" rx="2" />'
        '<path d="M9 4.5V4a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 4v.5" />'
        '<path d="M9 11.3 11 13.3l4-4.6" />'
    ),
    "heart": (
        '<path d="M12 19.5s-6.8-4.3-9-8.4C1.3 8 2.6 5 5.4 4.3c1.9-.5 3.6.5 4.8 2.2 '
        '1.2-1.7 2.9-2.7 4.8-2.2 2.8.7 4.1 3.7 2.4 6.8-2.2 4.1-9 8.4-9 8.4Z" />'
    ),
    "chevron-down": '<path d="m6 9 6 6 6-6" />',
    "log-out": (
        '<path d="M9 21H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3" />'
        '<path d="m16 17 5-5-5-5" />'
        '<path d="M21 12H9" />'
    ),
    "menu": '<path d="M4 6h16M4 12h16M4 18h16" />',
    "check": '<path d="m5 13 4.5 4.5L19 8" />',
    "calendar": (
        '<rect x="3.5" y="5" width="17" height="15.5" rx="2" />'
        '<path d="M3.5 9.5h17" />'
        '<path d="M8 3v4M16 3v4" />'
    ),
    "plus": '<path d="M12 5v14M5 12h14" />',
    "pencil": (
        '<path d="M4 20h4L19.5 8.5a2 2 0 0 0 0-2.83l-1.17-1.17a2 2 0 0 0-2.83 0L4 16v4Z" />'
        '<path d="M13.5 6.5l4 4" />'
    ),
    "trash": (
        '<path d="M5 7h14" />'
        '<path d="M9.5 7V5a1.5 1.5 0 0 1 1.5-1.5h2A1.5 1.5 0 0 1 14.5 5v2" />'
        '<path d="M7 7l.8 12a2 2 0 0 0 2 1.9h4.4a2 2 0 0 0 2-1.9L17 7" />'
        '<path d="M10.2 11v6M13.8 11v6" />'
    ),
    "search": (
        '<circle cx="11" cy="11" r="7" />'
        '<path d="m20 20-3.2-3.2" />'
    ),
}


@register.simple_tag
def icon(name, cls="shrink-0 w-[18px] h-[18px]"):
    path = _ICON_PATHS.get(name, "")
    return mark_safe(
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )
