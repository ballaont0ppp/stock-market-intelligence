"""Command-line interface for diagram generation."""

import argparse
import sys
import time
from pathlib import Path

from diagram_generator.core.config import ConfigManager
from diagram_generator.core.orchestrator import DiagramOrchestrator
from diagram_generator.core.types import DiagramType


class ProgressReporter:
    """Progress reporter for CLI operations."""
    
    def __init__(self):
        self.start_time = None
        self.last_update = 0
    
    def start(self, message: str):
        """Start progress reporting."""
        self.start_time = time.time()
        print(f"🔄 {message}...")
        sys.stdout.flush()
    
    def update(self, current: int, total: int, message: str = ""):
        """Update progress."""
        now = time.time()
        if now - self.last_update < 0.1:  # Throttle updates
            return
        
        self.last_update = now
        percent = (current / total * 100) if total > 0 else 0
        elapsed = now - self.start_time if self.start_time else 0
        
        # Format progress bar
        bar_length = 30
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        status = f"\r{message}: |{bar}| {percent:.1f}% ({current}/{total}) {elapsed:.1f}s"
        print(status, end="", flush=True)
    
    def finish(self, message: str, success: bool = True):
        """Finish progress reporting."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            icon = "✅" if success else "❌"
            print(f"\n{icon} {message} completed in {elapsed:.2f}s")
        else:
            print(f"\n{icon} {message}")
    
    def info(self, message: str):
        """Show informational message."""
        print(f"\nℹ️  {message}")
    
    def warning(self, message: str):
        """Show warning message."""
        print(f"\n⚠️  {message}")
    
    def error(self, message: str):
        """Show error message."""
        print(f"\n❌ {message}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate software diagrams from code"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate all diagrams')
    generate_parser.add_argument(
        '--source', '-s',
        default='.',
        help='Source directory to analyze (default: current directory)'
    )
    generate_parser.add_argument(
        '--config', '-c',
        help='Path to configuration file'
    )
    generate_parser.add_argument(
        '--output', '-o',
        default='diagrams',
        help='Output directory for diagrams (default: diagrams)'
    )
    generate_parser.add_argument(
        '--diagram-type', '-d',
        action='append',
        help='Specific diagram type to generate (can be used multiple times)'
    )
    generate_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    generate_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-essential output'
    )
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update diagrams incrementally')
    update_parser.add_argument(
        '--config', '-c',
        help='Path to configuration file'
    )
    update_parser.add_argument(
        '--since',
        help='Check for changes since timestamp (ISO format) or "1h", "1d", etc.'
    )
    update_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate diagram syntax')
    validate_parser.add_argument(
        'diagram_file',
        help='Path to diagram file to validate'
    )
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument(
        '--show',
        action='store_true',
        help='Show current configuration'
    )
    config_parser.add_argument(
        '--validate',
        help='Validate configuration file'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle commands
    if args.command == 'generate':
        return cmd_generate(args)
    elif args.command == 'update':
        return cmd_update(args)
    elif args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'config':
        return cmd_config(args)
    
    return 0


def cmd_generate(args):
    """Handle generate command."""
    progress = ProgressReporter()
    
    try:
        # Load configuration
        progress.start("Loading configuration")
        config_manager = ConfigManager()
        if args.config:
            config = config_manager.load_config(args.config)
        else:
            config = config_manager.get_config()
        
        # Override output directory if specified
        if args.output:
            config.output_dir = args.output
        
        progress.info(f"Source directory: {config.source_dir}")
        progress.info(f"Output directory: {config.output_dir}")
        progress.info(f"Enabled diagrams: {len(config.enabled_diagrams)}")
        
        # Create orchestrator and generate
        progress.start("Analyzing codebase")
        orchestrator = DiagramOrchestrator(config)
        result = orchestrator.generate_all_diagrams(config.source_dir)
        
        # Report results with progress
        progress.finish(f"Generated {len(result.diagrams)} diagrams", len(result.errors) == 0)
        
        if result.diagrams:
            print(f"\n📊 Generated diagrams:")
            for i, diagram in enumerate(result.diagrams, 1):
                print(f"  {i}. {diagram.title}")
        
        if result.errors:
            progress.error(f"Generation failed with {len(result.errors)} errors:")
            for error in result.errors:
                print(f"  - {error}")
            return 1
        
        if result.warnings:
            progress.warning(f"Generated with {len(result.warnings)} warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print(f"\n💾 Diagrams saved to: {config.output_dir}")
        return 0
    
    except Exception as e:
        progress.error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_update(args):
    """Handle update command."""
    progress = ProgressReporter()
    
    try:
        # Load configuration
        progress.start("Loading configuration")
        config_manager = ConfigManager()
        if args.config:
            config = config_manager.load_config(args.config)
        else:
            config = config_manager.get_config()
        
        # Create orchestrator
        progress.start("Creating orchestrator")
        orchestrator = DiagramOrchestrator(config)
        
        # Detect changes
        progress.start("Detecting file changes")
        from datetime import datetime, timedelta
        
        # Parse since parameter if provided
        if args.since:
            try:
                if args.since.endswith('h'):
                    hours = int(args.since[:-1])
                    last_gen = datetime.now() - timedelta(hours=hours)
                elif args.since.endswith('d'):
                    days = int(args.since[:-1])
                    last_gen = datetime.now() - timedelta(days=days)
                else:
                    # Try to parse as ISO timestamp
                    last_gen = datetime.fromisoformat(args.since.replace('Z', '+00:00'))
            except ValueError:
                print(f"Warning: Could not parse since parameter '{args.since}', using 24 hours")
                last_gen = datetime.now() - timedelta(hours=24)
        else:
            last_gen = datetime.now() - timedelta(hours=24)  # Last 24 hours for updates
        
        changes = orchestrator.change_detector.detect_changes(last_gen, config.source_dir)
        change_summary = orchestrator.change_detector.get_change_summary(changes)
        
        if change_summary == "No changes detected":
            progress.info("No changes detected since last generation")
            progress.finish("Update complete", True)
            return 0
        
        progress.info(f"Changes detected: {change_summary}")
        
        # Show detailed change info if verbose
        if hasattr(args, 'verbose') and args.verbose:
            for change_type, files in changes.items():
                if files:
                    progress.info(f"{change_type.title()}: {len(files)} file(s)")
                    for file_path in files[:3]:  # Show first 3
                        print(f"  - {file_path}")
                    if len(files) > 3:
                        print(f"  ... and {len(files) - 3} more")
        
        # Determine affected diagrams
        progress.start("Determining affected diagrams")
        affected_types = orchestrator.change_detector.get_affected_diagrams(
            changes.get('changed', []),
            changes.get('added', []),
            changes.get('deleted', [])
        )
        progress.info(f"Affected diagram types: {len(affected_types)}")
        
        # Update diagrams with progress
        total_diagrams = len([dt for dt in affected_types if dt in config.enabled_diagrams])
        if total_diagrams == 0:
            progress.info("No diagrams need updating")
            progress.finish("Update complete", True)
            return 0
        
        progress.start(f"Updating {total_diagrams} diagrams")
        result = orchestrator.update_diagrams(changes)
        
        progress.finish(f"Updated {len(result.diagrams)} diagrams", len(result.errors) == 0)
        
        if result.diagrams:
            print(f"\n🔄 Updated diagrams:")
            for diagram in result.diagrams:
                print(f"  - {diagram.title}")
        
        if result.errors:
            progress.error(f"Update failed with {len(result.errors)} errors:")
            for error in result.errors:
                print(f"  - {error}")
            return 1
        
        print(f"\n💾 Updated diagrams saved to: {config.output_dir}")
        return 0
    
    except Exception as e:
        progress.error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_validate(args):
    """Handle validate command."""
    print(f"Validating {args.diagram_file}...")
    
    try:
        from diagram_generator.formatters.mermaid_formatter import MermaidFormatter
        
        # Read diagram file
        with open(args.diagram_file, 'r') as f:
            content = f.read()
        
        # Extract Mermaid code from markdown
        # Look for ```mermaid blocks
        import re
        match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
        
        if not match:
            print("No Mermaid diagram found in file")
            return 1
        
        mermaid_code = match.group(1)
        
        # Validate
        formatter = MermaidFormatter()
        result = formatter.validate_syntax(mermaid_code)
        
        if result.is_valid:
            print("✓ Diagram syntax is valid")
            return 0
        else:
            print("✗ Diagram syntax is invalid")
            for error in result.errors:
                print(f"  Error: {error}")
            for warning in result.warnings:
                print(f"  Warning: {warning}")
            return 1
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def cmd_config(args):
    """Handle config command."""
    if args.show:
        try:
            config_manager = ConfigManager()
            config = config_manager.get_config()
            
            print("Current Configuration:")
            print(f"  Source Directory: {config.source_dir}")
            print(f"  Output Directory: {config.output_dir}")
            print(f"  Enabled Diagrams: {len(config.enabled_diagrams)}")
            for dt in config.enabled_diagrams:
                print(f"    - {dt.value}")
            print(f"  Create Backups: {config.create_backups}")
            print(f"  Preserve Manual Edits: {config.preserve_manual_edits}")
            
            return 0
        
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
