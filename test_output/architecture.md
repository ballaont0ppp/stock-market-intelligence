# System Architecture

## Metadata
- Generated: 2025-11-27 18:57:31.101900
- Generator Version: 0.1.0
- Source Files: 43

## Diagram

```mermaid
graph TD
    diagram_generator.cli[diagram_generator.cli]
    diagram_generator.setup[diagram_generator.setup]
    diagram_generator.__init__[diagram_generator.__init__]
    diagram_generator.analyzers.code_analyzer[diagram_generator.analyzers.code_analyzer]
    diagram_generator.analyzers.database_analyzer[diagram_generator.analyzers.database_analyzer]
    diagram_generator.analyzers.dependency_analyzer[diagram_generator.analyzers.dependency_analyzer]
    diagram_generator.analyzers.metadata_extractor[diagram_generator.analyzers.metadata_extractor]
    diagram_generator.analyzers.route_analyzer[diagram_generator.analyzers.route_analyzer]
    diagram_generator.analyzers.__init__[diagram_generator.analyzers.__init__]
    diagram_generator.core.base_generator[diagram_generator.core.base_generator]
    diagram_generator.core.config[diagram_generator.core.config]
    diagram_generator.core.exceptions[diagram_generator.core.exceptions]
    diagram_generator.core.orchestrator[diagram_generator.core.orchestrator]
    diagram_generator.core.types[diagram_generator.core.types]
    diagram_generator.core.__init__[diagram_generator.core.__init__]
    diagram_generator.formatters.mermaid_formatter[diagram_generator.formatters.mermaid_formatter]
    diagram_generator.formatters.__init__[diagram_generator.formatters.__init__]
    diagram_generator.generators.activity_generator[diagram_generator.generators.activity_generator]
    diagram_generator.generators.architecture_generator[diagram_generator.generators.architecture_generator]
    diagram_generator.generators.class_generator[diagram_generator.generators.class_generator]
    diagram_generator.generators.component_generator[diagram_generator.generators.component_generator]
    diagram_generator.generators.coverage_generator[diagram_generator.generators.coverage_generator]
    diagram_generator.generators.dataflow_generator[diagram_generator.generators.dataflow_generator]
    diagram_generator.generators.deployment_generator[diagram_generator.generators.deployment_generator]
    diagram_generator.generators.er_generator[diagram_generator.generators.er_generator]
    diagram_generator.generators.package_generator[diagram_generator.generators.package_generator]
    diagram_generator.generators.sequence_generator[diagram_generator.generators.sequence_generator]
    diagram_generator.generators.state_generator[diagram_generator.generators.state_generator]
    diagram_generator.generators.usecase_generator[diagram_generator.generators.usecase_generator]
    diagram_generator.generators.__init__[diagram_generator.generators.__init__]
    diagram_generator.tests.conftest[diagram_generator.tests.conftest]
    diagram_generator.tests.test_architecture_generator_properties[diagram_generator.tests.test_architecture_generator_properties]
    diagram_generator.tests.test_change_detector_properties[diagram_generator.tests.test_change_detector_properties]
    diagram_generator.tests.test_code_analyzer_properties[diagram_generator.tests.test_code_analyzer_properties]
    diagram_generator.tests.test_config_properties[diagram_generator.tests.test_config_properties]
    diagram_generator.tests.test_database_analyzer_properties[diagram_generator.tests.test_database_analyzer_properties]
    diagram_generator.tests.test_metadata_extractor_properties[diagram_generator.tests.test_metadata_extractor_properties]
    diagram_generator.tests.test_package_generator_properties[diagram_generator.tests.test_package_generator_properties]
    diagram_generator.tests.test_route_analyzer_properties[diagram_generator.tests.test_route_analyzer_properties]
    diagram_generator.tests.__init__[diagram_generator.tests.__init__]
    diagram_generator.utils.change_detector[diagram_generator.utils.change_detector]
    diagram_generator.utils.file_manager[diagram_generator.utils.file_manager]
    diagram_generator.utils.__init__[diagram_generator.utils.__init__]
    collections[collections]
    hypothesis[hypothesis]
    setuptools[setuptools]
    time[time]
    traceback[traceback]
    dataclasses[dataclasses]
    os[os]
    unittest[unittest]
    tempfile[tempfile]
    json[json]
    argparse[argparse]
    ast[ast]
    yaml[yaml]
    typing[typing]
    pytest[pytest]
    shutil[shutil]
    abc[abc]
    fnmatch[fnmatch]
    enum[enum]
    datetime[datetime]
    hashlib[hashlib]
    pathlib[pathlib]
    logging[logging]
    sys[sys]
    diagram_generator.cli --> diagram_generator.core.config
    diagram_generator.cli --> diagram_generator.core.orchestrator
    diagram_generator.cli --> diagram_generator.core.types
    diagram_generator.cli --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.cli --> re
    diagram_generator.analyzers.code_analyzer --> diagram_generator.core.types
    diagram_generator.analyzers.code_analyzer --> diagram_generator.core.exceptions
    diagram_generator.analyzers.database_analyzer --> re
    diagram_generator.analyzers.database_analyzer --> diagram_generator.core.types
    diagram_generator.analyzers.database_analyzer --> diagram_generator.core.exceptions
    diagram_generator.analyzers.database_analyzer --> diagram_generator.analyzers.code_analyzer
    diagram_generator.analyzers.dependency_analyzer --> diagram_generator.core.types
    diagram_generator.analyzers.metadata_extractor --> re
    diagram_generator.analyzers.metadata_extractor --> diagram_generator.core.types
    diagram_generator.analyzers.route_analyzer --> re
    diagram_generator.analyzers.route_analyzer --> diagram_generator.core.types
    diagram_generator.analyzers.route_analyzer --> diagram_generator.analyzers.code_analyzer
    diagram_generator.core.base_generator --> types
    diagram_generator.core.config --> types
    diagram_generator.core.config --> exceptions
    diagram_generator.core.orchestrator --> diagram_generator.core.types
    diagram_generator.core.orchestrator --> diagram_generator.core.config
    diagram_generator.core.orchestrator --> diagram_generator.analyzers.code_analyzer
    diagram_generator.core.orchestrator --> diagram_generator.analyzers.database_analyzer
    diagram_generator.core.orchestrator --> diagram_generator.analyzers.route_analyzer
    diagram_generator.core.orchestrator --> diagram_generator.analyzers.dependency_analyzer
    diagram_generator.core.orchestrator --> diagram_generator.analyzers.metadata_extractor
    diagram_generator.core.orchestrator --> diagram_generator.utils.file_manager
    diagram_generator.core.orchestrator --> diagram_generator.utils.change_detector
    diagram_generator.core.orchestrator --> diagram_generator.core.exceptions
    diagram_generator.core.orchestrator --> diagram_generator.generators.architecture_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.er_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.class_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.sequence_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.component_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.package_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.dataflow_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.state_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.usecase_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.deployment_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.activity_generator
    diagram_generator.core.orchestrator --> diagram_generator.generators.coverage_generator
    diagram_generator.formatters.mermaid_formatter --> re
    diagram_generator.formatters.mermaid_formatter --> diagram_generator.core.types
    diagram_generator.generators.activity_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.activity_generator --> diagram_generator.core.types
    diagram_generator.generators.activity_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.architecture_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.architecture_generator --> diagram_generator.core.types
    diagram_generator.generators.architecture_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.class_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.class_generator --> diagram_generator.core.types
    diagram_generator.generators.class_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.component_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.component_generator --> diagram_generator.core.types
    diagram_generator.generators.component_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.coverage_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.coverage_generator --> diagram_generator.core.types
    diagram_generator.generators.coverage_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.dataflow_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.dataflow_generator --> diagram_generator.core.types
    diagram_generator.generators.dataflow_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.deployment_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.deployment_generator --> diagram_generator.core.types
    diagram_generator.generators.deployment_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.er_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.er_generator --> diagram_generator.core.types
    diagram_generator.generators.er_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.package_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.package_generator --> diagram_generator.core.types
    diagram_generator.generators.package_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.sequence_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.sequence_generator --> diagram_generator.core.types
    diagram_generator.generators.sequence_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.state_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.state_generator --> diagram_generator.core.types
    diagram_generator.generators.state_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.usecase_generator --> diagram_generator.core.base_generator
    diagram_generator.generators.usecase_generator --> diagram_generator.core.types
    diagram_generator.generators.usecase_generator --> diagram_generator.formatters.mermaid_formatter
    diagram_generator.generators.__init__ --> architecture_generator
    diagram_generator.generators.__init__ --> er_generator
    diagram_generator.tests.test_architecture_generator_properties --> diagram_generator.generators.architecture_generator
    diagram_generator.tests.test_architecture_generator_properties --> diagram_generator.core.types
    diagram_generator.tests.test_change_detector_properties --> diagram_generator.utils.change_detector
    diagram_generator.tests.test_change_detector_properties --> diagram_generator.core.types
    diagram_generator.tests.test_code_analyzer_properties --> diagram_generator.analyzers.code_analyzer
    diagram_generator.tests.test_config_properties --> diagram_generator.core.config
    diagram_generator.tests.test_config_properties --> diagram_generator.core.types
    diagram_generator.tests.test_config_properties --> diagram_generator.core.exceptions
    diagram_generator.tests.test_database_analyzer_properties --> diagram_generator.analyzers.database_analyzer
    diagram_generator.tests.test_metadata_extractor_properties --> diagram_generator.analyzers.metadata_extractor
    diagram_generator.tests.test_metadata_extractor_properties --> diagram_generator.analyzers.code_analyzer
    diagram_generator.tests.test_package_generator_properties --> diagram_generator.generators.package_generator
    diagram_generator.tests.test_package_generator_properties --> diagram_generator.core.types
    diagram_generator.tests.test_route_analyzer_properties --> diagram_generator.analyzers.route_analyzer
    diagram_generator.utils.change_detector --> diagram_generator.core.types
    diagram_generator.utils.file_manager --> diagram_generator.core.types
    diagram_generator.utils.file_manager --> diagram_generator.core.exceptions
```

## Source Files
- diagram_generator\cli.py
- diagram_generator\setup.py
- diagram_generator\__init__.py
- diagram_generator\analyzers\code_analyzer.py
- diagram_generator\analyzers\database_analyzer.py
- diagram_generator\analyzers\dependency_analyzer.py
- diagram_generator\analyzers\metadata_extractor.py
- diagram_generator\analyzers\route_analyzer.py
- diagram_generator\analyzers\__init__.py
- diagram_generator\core\base_generator.py
- diagram_generator\core\config.py
- diagram_generator\core\exceptions.py
- diagram_generator\core\orchestrator.py
- diagram_generator\core\types.py
- diagram_generator\core\__init__.py
- diagram_generator\formatters\mermaid_formatter.py
- diagram_generator\formatters\__init__.py
- diagram_generator\generators\activity_generator.py
- diagram_generator\generators\architecture_generator.py
- diagram_generator\generators\class_generator.py
- diagram_generator\generators\component_generator.py
- diagram_generator\generators\coverage_generator.py
- diagram_generator\generators\dataflow_generator.py
- diagram_generator\generators\deployment_generator.py
- diagram_generator\generators\er_generator.py
- diagram_generator\generators\package_generator.py
- diagram_generator\generators\sequence_generator.py
- diagram_generator\generators\state_generator.py
- diagram_generator\generators\usecase_generator.py
- diagram_generator\generators\__init__.py
- diagram_generator\tests\conftest.py
- diagram_generator\tests\test_architecture_generator_properties.py
- diagram_generator\tests\test_change_detector_properties.py
- diagram_generator\tests\test_code_analyzer_properties.py
- diagram_generator\tests\test_config_properties.py
- diagram_generator\tests\test_database_analyzer_properties.py
- diagram_generator\tests\test_metadata_extractor_properties.py
- diagram_generator\tests\test_package_generator_properties.py
- diagram_generator\tests\test_route_analyzer_properties.py
- diagram_generator\tests\__init__.py
- diagram_generator\utils\change_detector.py
- diagram_generator\utils\file_manager.py
- diagram_generator\utils\__init__.py
