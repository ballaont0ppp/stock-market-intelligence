"""Route analyzer for extracting Flask route information."""

import ast
import re
from typing import List, Optional

from diagram_generator.core.types import (
    RouteMap,
    Endpoint,
    RequestFlow,
    AuthInfo,
    FileAnalysis,
    Participant,
    Message,
    DBOperation,
    ExternalCall,
)
from diagram_generator.analyzers.code_analyzer import CodeAnalyzer


class RouteAnalyzer:
    """Analyzes Flask routes and request flows."""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
    
    def analyze_routes(self, route_files: List[str]) -> RouteMap:
        """Analyze Flask route definitions.
        
        Args:
            route_files: List of paths to route files
            
        Returns:
            RouteMap object containing all endpoints
        """
        endpoints = []
        
        for file_path in route_files:
            try:
                # Analyze the file
                analysis = self.code_analyzer.analyze_file(file_path)
                
                # Extract endpoints from the file
                file_endpoints = self.extract_endpoints(analysis)
                endpoints.extend(file_endpoints)
            
            except Exception as e:
                # Log error but continue with other files
                print(f"Warning: Error analyzing {file_path}: {str(e)}")
                continue
        
        return RouteMap(endpoints=endpoints)
    
    def extract_endpoints(self, file_analysis: FileAnalysis) -> List[Endpoint]:
        """Extract API endpoints from file analysis.
        
        Args:
            file_analysis: FileAnalysis object
            
        Returns:
            List of Endpoint objects
        """
        endpoints = []
        
        # Look for functions with route decorators
        for func in file_analysis.functions:
            endpoint = self._extract_endpoint_from_function(func)
            if endpoint:
                endpoints.append(endpoint)
        
        # Also check methods in classes (for class-based views)
        for class_info in file_analysis.classes:
            for method in class_info.methods:
                endpoint = self._extract_endpoint_from_function(method)
                if endpoint:
                    endpoints.append(endpoint)
        
        return endpoints
    
    def trace_request_flow(self, endpoint: Endpoint) -> RequestFlow:
        """Trace the flow of a request through the system.
        
        Args:
            endpoint: Endpoint object
            
        Returns:
            RequestFlow object describing the flow
        """
        # This is a simplified implementation
        # In a real implementation, we'd analyze the function body more deeply
        
        participants = [
            Participant(name="Client", type="actor"),
            Participant(name="Route Handler", type="service"),
        ]
        
        messages = [
            Message(
                from_participant="Client",
                to_participant="Route Handler",
                message=f"{endpoint.methods[0] if endpoint.methods else 'GET'} {endpoint.path}"
            )
        ]
        
        return RequestFlow(
            participants=participants,
            messages=messages,
            database_operations=[],
            external_calls=[]
        )
    
    def extract_auth_requirements(self, endpoint: Endpoint) -> AuthInfo:
        """Extract authentication/authorization requirements.
        
        Args:
            endpoint: Endpoint object
            
        Returns:
            AuthInfo object
        """
        return AuthInfo(
            required=endpoint.auth_required,
            roles=endpoint.roles
        )
    
    def _extract_endpoint_from_function(self, func) -> Optional[Endpoint]:
        """Extract endpoint information from a function."""
        # Look for route decorators
        route_decorator = None
        auth_decorator = None
        
        for decorator in func.decorators:
            if self._is_route_decorator(decorator):
                route_decorator = decorator
            elif self._is_auth_decorator(decorator):
                auth_decorator = decorator
        
        if not route_decorator:
            return None
        
        # Extract route path and methods
        path = self._extract_route_path(route_decorator)
        methods = self._extract_route_methods(route_decorator)
        
        # Extract auth requirements
        auth_required = auth_decorator is not None
        roles = self._extract_roles(auth_decorator) if auth_decorator else []
        
        # Create endpoint
        endpoint = Endpoint(
            path=path,
            methods=methods,
            handler_function=func.name,
            auth_required=auth_required,
            roles=roles,
            docstring=func.docstring
        )
        
        # Trace request flow
        endpoint.request_flow = self.trace_request_flow(endpoint)
        
        return endpoint
    
    def _is_route_decorator(self, decorator) -> bool:
        """Check if a decorator is a route decorator."""
        route_names = ['route', 'get', 'post', 'put', 'delete', 'patch']
        return any(name in decorator.name.lower() for name in route_names)
    
    def _is_auth_decorator(self, decorator) -> bool:
        """Check if a decorator is an authentication decorator."""
        auth_names = ['login_required', 'auth_required', 'requires_auth', 'authenticated']
        return any(name in decorator.name.lower() for name in auth_names)
    
    def _extract_route_path(self, decorator) -> str:
        """Extract route path from decorator."""
        # Look for path in decorator arguments
        if decorator.args:
            # First argument is usually the path
            return decorator.args[0].strip('"\'')
        
        return "/"
    
    def _extract_route_methods(self, decorator) -> List[str]:
        """Extract HTTP methods from decorator."""
        methods = []
        
        # Check decorator name for method
        name_lower = decorator.name.lower()
        if 'get' in name_lower:
            methods.append('GET')
        elif 'post' in name_lower:
            methods.append('POST')
        elif 'put' in name_lower:
            methods.append('PUT')
        elif 'delete' in name_lower:
            methods.append('DELETE')
        elif 'patch' in name_lower:
            methods.append('PATCH')
        
        # Check decorator kwargs for methods
        if 'methods' in decorator.kwargs:
            methods_arg = decorator.kwargs['methods']
            if isinstance(methods_arg, list):
                methods.extend(methods_arg)
        
        # Default to GET if no methods specified
        if not methods:
            methods = ['GET']
        
        return methods
    
    def _extract_roles(self, decorator) -> List[str]:
        """Extract required roles from auth decorator."""
        roles = []
        
        # Check decorator arguments for roles
        if decorator.args:
            for arg in decorator.args:
                if isinstance(arg, str):
                    roles.append(arg)
        
        # Check decorator kwargs for roles
        if 'roles' in decorator.kwargs:
            roles_arg = decorator.kwargs['roles']
            if isinstance(roles_arg, list):
                roles.extend(roles_arg)
            elif isinstance(roles_arg, str):
                roles.append(roles_arg)
        
        return roles
