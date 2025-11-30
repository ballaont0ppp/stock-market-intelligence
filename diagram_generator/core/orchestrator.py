"""Diagram orchestrator for coordinating diagram generation."""

import traceback
import logging
from typing import List, Optional, Dict
from pathlib import Path

from diagram_generator.core.types import (
    GenerationResult,
    GenerationStatus,
    Diagram,
    DiagramType,
    AnalysisData,
)
from diagram_generator.core.config import Config
from diagram_generator.analyzers.code_analyzer import CodeAnalyzer
from diagram_generator.analyzers.database_analyzer import DatabaseAnalyzer
from diagram_generator.analyzers.route_analyzer import RouteAnalyzer
from diagram_generator.analyzers.dependency_analyzer import DependencyAnalyzer
from diagram_generator.analyzers.metadata_extractor import MetadataExtractor
from diagram_generator.utils.file_manager import FileManager
from diagram_generator.utils.change_detector import ChangeDetector
from diagram_generator.core.exceptions import GenerationError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiagramOrchestrator:
    """Orchestrates the diagram generation pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
        self.code_analyzer = CodeAnalyzer()
        self.database_analyzer = DatabaseAnalyzer()
        self.route_analyzer = RouteAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.metadata_extractor = MetadataExtractor()
        self.file_manager = FileManager(config.output_dir)
        self.change_detector = ChangeDetector()
        self.status = GenerationStatus()
    
    def generate_all_diagrams(self, source_path: str) -> GenerationResult:
        """Generate all configured diagram types with enhanced error handling.
        
        Args:
            source_path: Path to source code directory
            
        Returns:
            GenerationResult with generated diagrams
        """
        result = GenerationResult()
        
        try:
            # Update status
            self.status.in_progress = True
            
            # Analyze the codebase with error handling
            analysis_data = self._analyze_codebase_with_recovery(source_path, result)
            
            if not analysis_data:
                logger.error("Failed to analyze codebase")
                return result
            
            # Generate each enabled diagram type with individual error handling
            successful_generations = 0
            for diagram_type in self.config.enabled_diagrams:
                try:
                    self.status.current_diagram = diagram_type
                    diagram = self.generate_diagram_with_recovery(diagram_type, source_path, analysis_data, result)
                    
                    if diagram:
                        result.diagrams.append(diagram)
                        self.status.completed_diagrams.append(diagram_type)
                        successful_generations += 1
                        
                        # Write diagram to file with error handling
                        self._write_diagram_with_recovery(diagram, diagram_type, result)
                
                except Exception as e:
                    self._handle_generation_error(diagram_type, e, result)
                    continue
            
            # Add summary information
            if successful_generations > 0:
                result.warnings.append(f"Successfully generated {successful_generations}/{len(self.config.enabled_diagrams)} diagrams")
                logger.info(f"Generated {successful_generations} diagrams")
            else:
                result.errors.append("No diagrams were successfully generated")
                logger.error("No diagrams were successfully generated")
            
            self.status.in_progress = False
            
        except Exception as e:
            self._handle_critical_error(e, result)
            self.status.in_progress = False
        
        return result
    
    def generate_diagram(
        self,
        diagram_type: DiagramType,
        source_path: str,
        analysis_data: Optional[AnalysisData] = None
    ) -> Optional[Diagram]:
        """Generate a specific diagram type.
        
        Args:
            diagram_type: Type of diagram to generate
            source_path: Path to source code
            analysis_data: Pre-analyzed data (optional)
            
        Returns:
            Generated Diagram or None
        """
        # If no analysis data provided, analyze the codebase
        if analysis_data is None:
            analysis_data = self._analyze_codebase(source_path)
        
        # Import generators dynamically
        from diagram_generator.generators.architecture_generator import ArchitectureDiagramGenerator
        from diagram_generator.generators.er_generator import ERDiagramGenerator
        from diagram_generator.generators.class_generator import ClassDiagramGenerator
        from diagram_generator.generators.sequence_generator import SequenceDiagramGenerator
        from diagram_generator.generators.component_generator import ComponentDiagramGenerator
        from diagram_generator.generators.package_generator import PackageDiagramGenerator
        from diagram_generator.generators.dataflow_generator import DataFlowDiagramGenerator
        from diagram_generator.generators.state_generator import StateDiagramGenerator
        from diagram_generator.generators.usecase_generator import UseCaseDiagramGenerator
        from diagram_generator.generators.deployment_generator import DeploymentDiagramGenerator
        from diagram_generator.generators.activity_generator import ActivityDiagramGenerator
        from diagram_generator.generators.coverage_generator import TestCoverageDiagramGenerator
        
        # Map diagram types to generators
        generator_map = {
            DiagramType.ARCHITECTURE: ArchitectureDiagramGenerator,
            DiagramType.ER_DIAGRAM: ERDiagramGenerator,
            DiagramType.CLASS_DIAGRAM: ClassDiagramGenerator,
            DiagramType.SEQUENCE_DIAGRAM: SequenceDiagramGenerator,
            DiagramType.COMPONENT: ComponentDiagramGenerator,
            DiagramType.PACKAGE: PackageDiagramGenerator,
            DiagramType.DATA_FLOW: DataFlowDiagramGenerator,
            DiagramType.STATE_DIAGRAM: StateDiagramGenerator,
            DiagramType.USE_CASE: UseCaseDiagramGenerator,
            DiagramType.DEPLOYMENT: DeploymentDiagramGenerator,
            DiagramType.ACTIVITY: ActivityDiagramGenerator,
            DiagramType.TEST_COVERAGE: TestCoverageDiagramGenerator,
        }
        
        # Get generator class
        generator_class = generator_map.get(diagram_type)
        if not generator_class:
            return None
        
        # Instantiate and generate
        try:
            generator = generator_class()
            diagram = generator.generate(analysis_data)
            return diagram
        except Exception as e:
            print(f"Warning: Error generating {diagram_type.value}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_diagrams(self, changes: Dict[str, List[str]]) -> GenerationResult:
        """Incrementally update diagrams based on changed files.
        
        Args:
            changes: Dictionary with keys 'changed', 'added', 'deleted' and lists of file paths
            
        Returns:
            GenerationResult with updated diagrams
        """
        result = GenerationResult()
        
        # Determine which diagrams are affected
        affected_types = self.change_detector.get_affected_diagrams(
            changes.get('changed', []),
            changes.get('added', []),
            changes.get('deleted', [])
        )
        
        # Check if we should regenerate all diagrams
        if self.change_detector.should_regenerate_all(changes):
            # Perform full regeneration
            result = self.generate_all_diagrams(self.config.source_dir)
            result.warnings.append("Performing full regeneration due to extensive changes")
            return result
        
        # Regenerate only affected diagrams
        for diagram_type in affected_types:
            if diagram_type in self.config.enabled_diagrams:
                try:
                    diagram = self.generate_diagram(diagram_type, self.config.source_dir)
                    if diagram:
                        result.diagrams.append(diagram)
                        
                        # Write diagram to file
                        output_path = self._get_output_path(diagram_type)
                        
                        # Create backup if configured
                        if self.config.create_backups:
                            self.file_manager.create_backup(output_path)
                        
                        self.file_manager.write_diagram(diagram, output_path)
                
                except Exception as e:
                    result.errors.append(f"Failed to update {diagram_type.value}: {str(e)}")
        
        return result
    
    def get_generation_status(self) -> GenerationStatus:
        """Get current generation status.
        
        Returns:
            GenerationStatus object
        """
        return self.status
    
    def _analyze_codebase(self, source_path: str) -> AnalysisData:
        """Analyze the codebase.
        
        Args:
            source_path: Path to source code
            
        Returns:
            AnalysisData object
        """
        analysis_data = AnalysisData()
        
        # Analyze directory
        dir_analysis = self.code_analyzer.analyze_directory(
            source_path,
            max_depth=self.config.max_depth
        )
        analysis_data.file_analyses = dir_analysis.file_analyses
        
        # Build dependency graph
        analysis_data.dependency_graph = self.dependency_analyzer.build_dependency_graph(
            dir_analysis.file_analyses
        )
        
        # Analyze database models
        model_files = [
            fa.file_path for fa in dir_analysis.file_analyses
            if 'model' in fa.file_path.lower()
        ]
        if model_files:
            analysis_data.database_schema = self.database_analyzer.analyze_models(model_files)
        
        # Analyze routes
        route_files = [
            fa.file_path for fa in dir_analysis.file_analyses
            if 'route' in fa.file_path.lower() or 'api' in fa.file_path.lower()
        ]
        if route_files:
            analysis_data.route_map = self.route_analyzer.analyze_routes(route_files)
        
        return analysis_data
    
    def _get_output_path(self, diagram_type: DiagramType) -> str:
        """Get output path for diagram type.
        
        Args:
            diagram_type: Type of diagram
            
        Returns:
            Output file path
        """
        filename = f"{diagram_type.value}.md"
        return str(Path(self.config.output_dir) / filename)
    
    def _analyze_codebase_with_recovery(self, source_path: str, result: GenerationResult) -> Optional[AnalysisData]:
        """Analyze the codebase with error recovery.
        
        Args:
            source_path: Path to source code
            result: GenerationResult to collect errors
            
        Returns:
            AnalysisData or None if failed
        """
        try:
            logger.info(f"Starting codebase analysis: {source_path}")
            return self._analyze_codebase(source_path)
        except Exception as e:
            error_msg = f"Failed to analyze codebase: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            logger.debug(traceback.format_exc())
            return None
    
    def generate_diagram_with_recovery(
        self, 
        diagram_type: DiagramType, 
        source_path: str, 
        analysis_data: AnalysisData,
        result: GenerationResult
    ) -> Optional[Diagram]:
        """Generate diagram with error recovery.
        
        Args:
            diagram_type: Type of diagram to generate
            source_path: Path to source code
            analysis_data: Pre-analyzed data
            result: GenerationResult to collect errors
            
        Returns:
            Generated Diagram or None
        """
        try:
            logger.info(f"Generating {diagram_type.value} diagram")
            return self.generate_diagram(diagram_type, source_path, analysis_data)
        except ImportError as e:
            error_msg = f"Missing dependencies for {diagram_type.value}: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            return None
        except Exception as e:
            error_msg = f"Error generating {diagram_type.value}: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            logger.debug(traceback.format_exc())
            return None
    
    def _write_diagram_with_recovery(self, diagram: Diagram, diagram_type: DiagramType, result: GenerationResult) -> None:
        """Write diagram to file with error recovery.
        
        Args:
            diagram: Diagram to write
            diagram_type: Type of diagram
            result: GenerationResult to collect errors
        """
        try:
            output_path = self._get_output_path(diagram_type)
            self.file_manager.write_diagram(diagram, output_path)
            logger.info(f"Successfully wrote {diagram_type.value} to {output_path}")
        except Exception as e:
            error_msg = f"Failed to write {diagram_type.value}: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
    
    def _handle_generation_error(self, diagram_type: DiagramType, error: Exception, result: GenerationResult) -> None:
        """Handle diagram generation errors.
        
        Args:
            diagram_type: Type of diagram that failed
            error: Exception that occurred
            result: GenerationResult to collect errors
        """
        error_msg = f"Failed to generate {diagram_type.value}: {str(error)}"
        logger.error(error_msg)
        result.errors.append(error_msg)
        self.status.failed_diagrams.append(diagram_type)
        
        # Add context for common error types
        if isinstance(error, ImportError):
            result.warnings.append(f"Missing dependencies for {diagram_type.value} - some features may be unavailable")
        elif isinstance(error, PermissionError):
            result.warnings.append(f"Permission denied writing {diagram_type.value} - check file permissions")
        elif isinstance(error, FileNotFoundError):
            result.warnings.append(f"Required files missing for {diagram_type.value}")
        
        logger.debug(traceback.format_exc())
    
    def _handle_critical_error(self, error: Exception, result: GenerationResult) -> None:
        """Handle critical errors that stop the entire generation process.
        
        Args:
            error: Exception that occurred
            result: GenerationResult to collect errors
        """
        error_msg = f"Critical error during generation: {str(error)}"
        logger.error(error_msg)
        result.errors.append(error_msg)
        
        # Add recovery suggestions
        result.warnings.append("Try running with verbose mode (-v) for more details")
        result.warnings.append("Check that all dependencies are installed")
        result.warnings.append("Verify source directory permissions")
        
        logger.debug(traceback.format_exc())
    
    def get_detailed_error_report(self, result: GenerationResult) -> str:
        """Generate a detailed error report.
        
        Args:
            result: GenerationResult with errors
            
        Returns:
            Formatted error report
        """
        report_lines = ["=== Diagram Generation Error Report ==="]
        report_lines.append(f"Total errors: {len(result.errors)}")
        report_lines.append(f"Total warnings: {len(result.warnings)}")
        report_lines.append("")
        
        if result.errors:
            report_lines.append("ERRORS:")
            for i, error in enumerate(result.errors, 1):
                report_lines.append(f"  {i}. {error}")
            report_lines.append("")
        
        if result.warnings:
            report_lines.append("WARNINGS:")
            for i, warning in enumerate(result.warnings, 1):
                report_lines.append(f"  {i}. {warning}")
            report_lines.append("")
        
        report_lines.append("=== Recovery Suggestions ===")
        report_lines.append("1. Check source directory exists and is readable")
        report_lines.append("2. Verify all Python dependencies are installed")
        report_lines.append("3. Ensure write permissions for output directory")
        report_lines.append("4. Try generating diagrams individually")
        report_lines.append("5. Check logs for detailed error information")
        
        return "\n".join(report_lines)
