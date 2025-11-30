"""Change detector for monitoring file system changes."""

from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict, Optional
import hashlib
import json

from diagram_generator.core.types import Diagram, DiagramType


class ChangeDetector:
    """Detects file system changes for incremental updates."""
    
    def __init__(self, config=None):
        self._file_hashes: Dict[str, str] = {}
        self._known_files: Set[str] = set()
        self.config = config
        self._state_file = ".diagram_generator_state.json"
    
    def detect_changes(self, last_generation: datetime, source_dir: str = ".") -> Dict[str, List[str]]:
        """Detect changed, added, and deleted files since last generation.
        
        Args:
            last_generation: Timestamp of last generation
            source_dir: Source directory to monitor
            
        Returns:
            Dictionary with keys: 'changed', 'added', 'deleted'
        """
        source_path = Path(source_dir)
        current_files = set()
        changed_files = []
        added_files = []
        
        # Load previous state if available
        self._load_state(source_dir)
        
        # Find all Python files
        for py_file in source_path.rglob('*.py'):
            file_path = str(py_file.relative_to(source_path))
            current_files.add(file_path)
            
            # Check if file was modified after last generation
            mtime = datetime.fromtimestamp(py_file.stat().st_mtime)
            if mtime > last_generation:
                if file_path in self._known_files:
                    changed_files.append(file_path)
                else:
                    added_files.append(file_path)
        
        # Find deleted files
        deleted_files = list(self._known_files - current_files)
        
        # Update state
        self._known_files = current_files
        self._save_state(source_dir)
        
        return {
            'changed': changed_files,
            'added': added_files,
            'deleted': deleted_files
        }
    
    def scan_directory(self, source_dir: str = ".") -> List[str]:
        """Scan directory and return all Python files.
        
        Args:
            source_dir: Source directory to scan
            
        Returns:
            List of Python file paths relative to source directory
        """
        source_path = Path(source_dir)
        python_files = []
        
        for py_file in source_path.rglob('*.py'):
            file_path = str(py_file.relative_to(source_path))
            python_files.append(file_path)
        
        return sorted(python_files)
    
    def get_affected_diagrams(self, changed_files: List[str], 
                             added_files: Optional[List[str]] = None,
                             deleted_files: Optional[List[str]] = None) -> List[DiagramType]:
        """Determine which diagrams are affected by changes, additions, and deletions.
        
        Args:
            changed_files: List of changed file paths
            added_files: List of added file paths (optional)
            deleted_files: List of deleted file paths (optional)
            
        Returns:
            List of affected DiagramType values
        """
        if added_files is None:
            added_files = []
        if deleted_files is None:
            deleted_files = []
            
        affected = set()
        
        # Analyze all types of changes
        all_changes = changed_files + added_files + deleted_files
        
        for file_path in all_changes:
            path_lower = file_path.lower()
            
            # Database-related files affect ER diagrams
            if any(keyword in path_lower for keyword in ['model', 'db', 'database', 'entity', 'schema']):
                affected.add(DiagramType.ER_DIAGRAM)
            
            # Route/API files affect sequence and use case diagrams
            if any(keyword in path_lower for keyword in ['route', 'api', 'endpoint', 'controller', 'view']):
                affected.add(DiagramType.SEQUENCE_DIAGRAM)
                affected.add(DiagramType.USE_CASE)
            
            # Test files affect test coverage diagrams
            if any(keyword in path_lower for keyword in ['test', 'spec', '_test', '_spec']):
                affected.add(DiagramType.TEST_COVERAGE)
            
            # Configuration files affect deployment diagrams
            if any(keyword in path_lower for keyword in ['config', 'deployment', 'docker', 'compose']):
                affected.add(DiagramType.DEPLOYMENT)
            
            # Activity/workflow files affect activity diagrams
            if any(keyword in path_lower for keyword in ['workflow', 'process', 'service', 'job', 'task']):
                affected.add(DiagramType.ACTIVITY)
            
            # State-related files affect state diagrams
            if any(keyword in path_lower for keyword in ['state', 'statemachine', 'fsm']):
                affected.add(DiagramType.STATE_DIAGRAM)
            
            # Any file changes can affect package structure
            affected.add(DiagramType.PACKAGE)
            
            # Any Python file affects class diagrams
            if file_path.endswith('.py'):
                affected.add(DiagramType.CLASS_DIAGRAM)
            
            # All changes affect architecture, component, and data flow diagrams
            affected.add(DiagramType.ARCHITECTURE)
            affected.add(DiagramType.COMPONENT)
            affected.add(DiagramType.DATA_FLOW)
        
        return list(affected)
    
    def should_regenerate(self, diagram: Diagram, changes: List[str]) -> bool:
        """Determine if diagram needs regeneration.
        
        Args:
            diagram: Diagram to check
            changes: List of changed files
            
        Returns:
            True if diagram should be regenerated
        """
        # Check if any of the diagram's source files changed
        for source_file in diagram.source_files:
            if source_file in changes:
                return True
        
        return False
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate hash of file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            MD5 hash of file content
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def _load_state(self, source_dir: str):
        """Load state from file.
        
        Args:
            source_dir: Source directory to load state for
        """
        state_path = Path(source_dir) / self._state_file
        try:
            if state_path.exists():
                with open(state_path, 'r') as f:
                    state_data = json.load(f)
                    self._known_files = set(state_data.get('known_files', []))
                    self._file_hashes = state_data.get('file_hashes', {})
        except Exception:
            # If loading fails, start with empty state
            self._known_files = set()
            self._file_hashes = {}
    
    def _save_state(self, source_dir: str):
        """Save state to file.
        
        Args:
            source_dir: Source directory to save state for
        """
        state_path = Path(source_dir) / self._state_file
        try:
            state_data = {
                'known_files': list(self._known_files),
                'file_hashes': self._file_hashes,
                'last_updated': datetime.now().isoformat()
            }
            with open(state_path, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save state: {e}")
    
    def get_change_summary(self, changes: Dict[str, List[str]]) -> str:
        """Get a human-readable summary of changes.
        
        Args:
            changes: Dictionary of changes from detect_changes
            
        Returns:
            Summary string describing the changes
        """
        summary_parts = []
        
        if changes['changed']:
            summary_parts.append(f"{len(changes['changed'])} modified")
        
        if changes['added']:
            summary_parts.append(f"{len(changes['added'])} added")
        
        if changes['deleted']:
            summary_parts.append(f"{len(changes['deleted'])} deleted")
        
        if not summary_parts:
            return "No changes detected"
        
        return ", ".join(summary_parts) + " file(s)"
    
    def should_regenerate_all(self, changes: Dict[str, List[str]]) -> bool:
        """Determine if all diagrams should be regenerated.
        
        Args:
            changes: Dictionary of changes from detect_changes
            
        Returns:
            True if changes are extensive enough to warrant full regeneration
        """
        total_changes = len(changes['changed']) + len(changes['added']) + len(changes['deleted'])
        
        # Regenerate all if changes affect > 50% of files or > 10 files
        return total_changes > len(self._known_files) * 0.5 or total_changes > 10
