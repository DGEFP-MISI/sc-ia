import markdown
import nh3


ALLOWED_TAGS = {
    "p", "br", "strong", "em", "del",
    "h2", "h3", "h4",
    "ul", "ol", "li",
    "blockquote", "code", "pre",
    "table", "thead", "tbody", "tr", "th", "td",
    "a", "hr",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "th": {"align"},
    "td": {"align"},
}

ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


def render_assistant_markdown(content):
    """Convertit une réponse Markdown d'Albert en HTML assaini."""

    html = markdown.markdown(
        content,
        extensions=["extra", "sane_lists"],
    )

    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_PROTOCOLS,
        clean_content_tags={"script", "style"},
    )
