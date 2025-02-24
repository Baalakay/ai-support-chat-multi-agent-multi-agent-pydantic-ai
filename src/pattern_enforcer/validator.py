"""Pattern validation through static analysis."""
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from .errors import PatternViolationError, ValidationError


@dataclass
class ValidationResult:
    """Result of pattern validation."""
    valid: bool
    violations: List[str] = None
    messages: List[str] = None
    
    def __bool__(self) -> bool:
        return self.valid


class ASTPatternAnalyzer:
    """Analyzes Python AST for pattern validation."""
    
    def parse(self, file_path: str) -> ast.AST:
        """Parse Python file into AST."""
        try:
            with open(file_path, 'r') as f:
                return ast.parse(f.read(), filename=file_path)
        except Exception as e:
            raise ValidationError(f"Failed to parse {file_path}: {e}")
    
    def find_imports(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Find all imports in AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        'type': 'import',
                        'name': name.name,
                        'asname': name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    imports.append({
                        'type': 'from',
                        'module': node.module,
                        'name': name.name,
                        'asname': name.asname
                    })
        
        return imports
    
    def find_function_calls(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find all function calls in AST."""
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append({
                        'type': 'direct',
                        'name': node.func.id,
                        'args': len(node.args),
                        'keywords': len(node.keywords)
                    })
                elif isinstance(node.func, ast.Attribute):
                    calls.append({
                        'type': 'attribute',
                        'object': self._get_attribute_source(node.func),
                        'name': node.func.attr,
                        'args': len(node.args),
                        'keywords': len(node.keywords)
                    })
        
        return calls
    
    def _get_attribute_source(self, node: ast.Attribute) -> str:
        """Get the source object of an attribute."""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        
        return '.'.join(reversed(parts))


class PatternValidator:
    """Validates patterns through static analysis."""
    
    def __init__(self, rules_file: str):
        """Initialize validator with rules file."""
        self.rules = self._load_rules(rules_file)
        self.ast_analyzer = ASTPatternAnalyzer()
    
    def _load_rules(self, rules_file: str) -> Dict[str, Any]:
        """Load rules from MDC file."""
        try:
            with open(rules_file, 'r') as f:
                content = f.read()
                # Extract YAML blocks
                yaml_blocks = []
                in_yaml = False
                current_block = []
                
                for line in content.split('\n'):
                    if line.strip() == '```yaml':
                        in_yaml = True
                    elif line.strip() == '```' and in_yaml:
                        in_yaml = False
                        if current_block:
                            yaml_blocks.append('\n'.join(current_block))
                            current_block = []
                    elif in_yaml:
                        current_block.append(line)
                
                # Parse YAML blocks
                rules = {}
                for block in yaml_blocks:
                    try:
                        data = yaml.safe_load(block)
                        if isinstance(data, dict):
                            rules.update(data)
                    except yaml.YAMLError:
                        continue
                
                return rules
        except Exception as e:
            raise ValidationError(f"Failed to load rules from {rules_file}: {e}")
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """Analyze file for pattern compliance."""
        try:
            # Parse file to AST
            ast = self.ast_analyzer.parse(file_path)
            
            # Get all imports and function calls
            imports = self.ast_analyzer.find_imports(ast)
            calls = self.ast_analyzer.find_function_calls(ast)
            
            # Check against blacklist
            blacklist_violations = self._check_blacklist(imports, calls)
            if blacklist_violations:
                return ValidationResult(
                    valid=False,
                    violations=blacklist_violations,
                    messages=["Blacklisted patterns found"]
                )
            
            # Verify required patterns
            missing_patterns = self._check_required(imports, calls)
            if missing_patterns:
                return ValidationResult(
                    valid=False,
                    violations=missing_patterns,
                    messages=["Missing required patterns"]
                )
            
            return ValidationResult(
                valid=True,
                messages=["All patterns validated"]
            )
            
        except Exception as e:
            raise ValidationError(f"Validation failed for {file_path}: {e}")
    
    def _check_blacklist(
        self,
        imports: List[Dict[str, str]],
        calls: List[Dict[str, Any]]
    ) -> List[str]:
        """Check for blacklisted patterns."""
        violations = []
        
        if 'BLACKLIST' in self.rules:
            blacklist = self.rules['BLACKLIST']
            for pattern in blacklist:
                # Check imports
                for imp in imports:
                    if imp['type'] == 'import' and pattern['pattern'] in imp['name']:
                        violations.append(
                            f"Blacklisted import: {imp['name']} ({pattern['reason']})"
                        )
                    elif imp['type'] == 'from' and pattern['pattern'] in f"{imp['module']}.{imp['name']}":
                        violations.append(
                            f"Blacklisted import: {imp['module']}.{imp['name']} ({pattern['reason']})"
                        )
                
                # Check function calls
                for call in calls:
                    if call['type'] == 'direct' and pattern['pattern'] in call['name']:
                        violations.append(
                            f"Blacklisted call: {call['name']} ({pattern['reason']})"
                        )
                    elif call['type'] == 'attribute' and pattern['pattern'] in f"{call['object']}.{call['name']}":
                        violations.append(
                            f"Blacklisted call: {call['object']}.{call['name']} ({pattern['reason']})"
                        )
        
        return violations
    
    def _check_required(
        self,
        imports: List[Dict[str, str]],
        calls: List[Dict[str, Any]]
    ) -> List[str]:
        """Check for required patterns."""
        missing = []
        
        if 'REQUIRED_PATTERNS' in self.rules:
            required = self.rules['REQUIRED_PATTERNS']
            for name, pattern in required.items():
                if 'pattern' in pattern:
                    # Split pattern into lines
                    pattern_lines = pattern['pattern'].strip().split('\n')
                    
                    # Check each line exists
                    for line in pattern_lines:
                        line = line.strip()
                        if line.startswith('import '):
                            module = line.split(' ')[1]
                            if not any(i['type'] == 'import' and i['name'] == module for i in imports):
                                missing.append(f"Missing required import: {line}")
                        elif line.startswith('from '):
                            parts = line.split(' ')
                            module = parts[1]
                            names = parts[3].split(',')
                            for name in names:
                                name = name.strip()
                                if not any(
                                    i['type'] == 'from' and
                                    i['module'] == module and
                                    i['name'] == name
                                    for i in imports
                                ):
                                    missing.append(f"Missing required import: {line}")
        
        return missing 