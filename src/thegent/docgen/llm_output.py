"""Generate LLM-friendly documentation (.llms.txt)."""

from pathlib import Path
from typing import Any


class LLMOutputGenerator:
    """Generate LLM-friendly documentation format."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize LLM output generator.
        
        Args:
            output_dir: Output directory for .llms.txt files
        """
        self.output_dir = output_dir or Path("docs/.llms")

    def generate_from_markdown(self, md_file: Path) -> Path:
        """Generate .llms.txt from markdown file.
        
        Args:
            md_file: Markdown file path
            
        Returns:
            Path to generated .llms.txt file
        """
        content = md_file.read_text()
        
        # Convert markdown to plain text (simplified)
        # In production, would use proper markdown parser
        text_content = self._markdown_to_text(content)
        
        # Add metadata header
        llms_content = f"""# LLM-Friendly Documentation
# Source: {md_file}
# Generated: {Path(__file__).stat().st_mtime}

{text_content}
"""
        
        # Write .llms.txt file
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / f"{md_file.stem}.llms.txt"
        output_file.write_text(llms_content)
        
        return output_file

    def _markdown_to_text(self, markdown: str) -> str:
        """Convert markdown to plain text.
        
        Args:
            markdown: Markdown content
            
        Returns:
            Plain text content
        """
        # Simple conversion - remove markdown syntax
        text = markdown
        # Remove headers
        import re
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
        # Remove code blocks
        text = re.sub(r"```[\w]*\n.*?```", "", text, flags=re.DOTALL)
        # Remove inline code
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Remove links but keep text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        
        return text

    def generate_batch(self, md_files: list[Path]) -> list[Path]:
        """Generate .llms.txt files for multiple markdown files.
        
        Args:
            md_files: List of markdown files
            
        Returns:
            List of generated .llms.txt file paths
        """
        generated = []
        for md_file in md_files:
            try:
                output_file = self.generate_from_markdown(md_file)
                generated.append(output_file)
            except Exception as e:
                print(f"Error generating LLM output for {md_file}: {e}")
        
        return generated
