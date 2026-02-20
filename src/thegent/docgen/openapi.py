"""Implement OpenAPI/Swagger integration for documentation."""

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class OpenAPIGenerator:
    """Generate OpenAPI/Swagger integration for documentation."""

    def __init__(self, output_format: str = "yaml") -> None:
        self.output_format = output_format

    def parse_openapi_spec(self, file_path: Path) -> dict[str, Any] | None:
        """Parse an OpenAPI spec file.

        Args:
            file_path: Spec file path

        Returns:
            Parsed spec dictionary
        """
        import json

        import yaml

        try:
            if file_path.suffix in {".yaml", ".yml"}:
                return yaml.safe_load(file_path.read_text())
            if file_path.suffix == ".json":
                return json.loads(file_path.read_text())
            logger.error(f"Unsupported file format {file_path.suffix}")
            return None
        except Exception as e:
            logger.error(f"Error parsing OpenAPI spec {file_path}: {e}")
            return None

    def generate_swagger_ui_html(self, spec_url: str) -> str:
        """Generate HTML for Swagger UI.

        Args:
            spec_url: URL to spec file

        Returns:
            Swagger UI HTML content
        """
        # Simple template for Swagger UI
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.1.3/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.1.3/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "{spec_url}",
                dom_id: '#swagger-ui',
            }});
        }}
    </script>
</body>
</html>
"""
