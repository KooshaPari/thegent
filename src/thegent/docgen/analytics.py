"""Implement Google Analytics / Plausible integration for documentation."""

import logging

logger = logging.getLogger(__name__)


class AnalyticsGenerator:
    """Generate analytics integration for documentation."""

    def __init__(self, google_analytics_id: str | None = None, plausible_domain: str | None = None) -> None:
        self.google_analytics_id = google_analytics_id
        self.plausible_domain = plausible_domain

    def generate_google_analytics_script(self) -> str:
        """Generate Google Analytics script tag.

        Returns:
            Google Analytics script tag HTML content
        """
        if not self.google_analytics_id:
            return ""

        script1 = f"https://www.googletagmanager.com/gtag/js?id={self.google_analytics_id}"
        script2 = f"""window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{self.google_analytics_id}');"""

        return f"""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="{script1}"></script>
<script>
{script2}
</script>
"""

    def generate_plausible_script(self) -> str:
        """Generate Plausible script tag.

        Returns:
            Plausible script tag HTML content
        """
        if not self.plausible_domain:
            return ""

        return f"""
<!-- Plausible Analytics -->
<script defer data-domain="{self.plausible_domain}" src="https://plausible.io/js/plausible.js"></script>
"""
