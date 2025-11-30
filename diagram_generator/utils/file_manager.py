"""File manager for writing and managing diagram files."""

from pathlib import Path
from datetime import datetime
from typing import Optional
import shutil

from diagram_generator.core.types import Diagram
from diagram_generator.core.exceptions import FileIOError


class FileManager:
    """Manages diagram file I/O and versioning."""
    
    def __init__(self, output_dir: str = "diagrams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_diagram(self, diagram: Diagram, output_path: str) -> None:
        """Write diagram to file.
        
        Args:
            diagram: Diagram object to write
            output_path: Path to write diagram to
            
        Raises:
            FileIOError: If writing fails
        """
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create markdown file with Mermaid code
            content = self._format_diagram_file(diagram)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        except Exception as e:
            raise FileIOError(
                f"Failed to write diagram to {output_path}: {str(e)}",
                {"output_path": output_path, "error": str(e)}
            )
    
    def read_existing_diagram(self, file_path: str) -> Optional[Diagram]:
        """Read existing diagram file.
        
        Args:
            file_path: Path to diagram file
            
        Returns:
            Diagram object or None if file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the diagram from markdown
            # This is simplified - in a real implementation,
            # we'd parse the metadata and Mermaid code
            return None  # Placeholder
        
        except Exception as e:
            raise FileIOError(
                f"Failed to read diagram from {file_path}: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
    
    def create_backup(self, file_path: str) -> str:
        """Create backup of existing diagram.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file
            
        Raises:
            FileIOError: If backup creation fails
        """
        path = Path(file_path)
        
        if not path.exists():
            return ""
        
        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = path.with_suffix(f".{timestamp}.bak")
            
            shutil.copy2(path, backup_path)
            
            return str(backup_path)
        
        except Exception as e:
            raise FileIOError(
                f"Failed to create backup of {file_path}: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
    
    def detect_manual_edits(self, file_path: str) -> bool:
        """Detect if a file has manual edits.
        
        Args:
            file_path: Path to diagram file
            
        Returns:
            True if manual edits detected
        """
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for manual edit markers
            if "<!-- MANUAL EDIT -->" in content:
                return True
            
            # Check if file was modified after generation
            # (simplified - would need to parse metadata)
            return False
        
        except Exception:
            return False
    
    def merge_manual_edits(self, generated: Diagram, existing: Diagram) -> Diagram:
        """Merge manual edits with generated content.
        
        Args:
            generated: Newly generated diagram
            existing: Existing diagram with potential manual edits
            
        Returns:
            Merged diagram
        """
        # Detect manual edits in existing diagram
        if existing and existing.metadata:
            # Check if existing has manual edit markers
            if existing.metadata.manual_edits:
                # Preserve manual edits by keeping existing content
                # and adding a note to the generated diagram
                generated.metadata.manual_edits = True
                
                # In a real implementation, we would:
                # 1. Parse both diagrams
                # 2. Identify manually added sections
                # 3. Merge them into the generated diagram
                # 4. Mark merged sections with comments
        
        return generated
    
    def _format_diagram_file(self, diagram: Diagram) -> str:
        """Format diagram as markdown file.
        
        Args:
            diagram: Diagram object
            
        Returns:
            Formatted markdown content
        """
        lines = []
        
        # Add title
        lines.append(f"# {diagram.title}")
        lines.append("")
        
        # Add metadata
        lines.append("## Metadata")
        lines.append(f"- Generated: {diagram.metadata.generated_at}")
        lines.append(f"- Generator Version: {diagram.metadata.generator_version}")
        lines.append(f"- Source Files: {len(diagram.source_files)}")
        lines.append("")
        
        # Add Mermaid diagram
        lines.append("## Diagram")
        lines.append("")
        lines.append("```mermaid")
        lines.append(diagram.mermaid_code)
        lines.append("```")
        lines.append("")
        
        # Add source files list
        if diagram.source_files:
            lines.append("## Source Files")
            for source_file in diagram.source_files:
                lines.append(f"- {source_file}")
            lines.append("")
        
        return "\n".join(lines)
