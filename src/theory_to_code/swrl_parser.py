#!/usr/bin/env python3
"""
SWRL Rule Parser for Theory-to-Code System

Parses natural language rule descriptions into SWRL atoms.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AtomType(Enum):
    """Types of SWRL atoms"""
    CLASS = "class"
    OBJECT_PROPERTY = "object_property"
    DATA_PROPERTY = "data_property"
    BUILTIN = "builtin"
    

@dataclass
class SWRLAtom:
    """Represents a SWRL atom"""
    atom_type: AtomType
    predicate: str
    arguments: List[str]
    
    def to_swrl(self) -> str:
        """Convert to SWRL syntax"""
        args = ", ".join(self.arguments)
        return f"{self.predicate}({args})"


@dataclass 
class ParsedRule:
    """Parsed SWRL rule"""
    antecedent: List[SWRLAtom]  # if/condition part
    consequent: List[SWRLAtom]  # then/consequence part
    variables: Set[str]
    confidence: float
    

class SWRLParser:
    """Parses natural language rules into SWRL"""
    
    def __init__(self):
        # Patterns for common social science rule structures
        # Updated to handle entity types like "Person ?x" or just "?x"
        entity_pattern = r"(?:(?:Person|Agent|Group|Entity)\s+)?(\?\w+|\w+)"
        
        self.patterns = {
            # "X belongs to Y" -> belongsTo(?x, ?y)
            f"{entity_pattern}\\s+belongs?\\s+to\\s+{entity_pattern}": ("belongsTo", ["subject", "object"]),
            
            # "X is in same group as Y" -> sameGroup(?x, ?y)
            f"{entity_pattern}\\s+is\\s+in\\s+same\\s+group\\s+as\\s+{entity_pattern}": ("sameGroup", ["subject", "object"]),
            
            # "X shows bias toward Y" -> showsBias(?x, ?y)
            f"{entity_pattern}\\s+shows?\\s+bias\\s+toward\\s+{entity_pattern}": ("showsBias", ["subject", "object"]),
            
            # "X shows out-group derogation toward Y" -> showsOutGroupDerogation(?x, ?y)
            f"{entity_pattern}\\s+shows?\\s+out-group\\s+derogation\\s+toward\\s+{entity_pattern}": ("showsOutGroupDerogation", ["subject", "object"]),
            
            # "X influences Y" -> influences(?x, ?y)
            f"{entity_pattern}\\s+influences?\\s+{entity_pattern}": ("influences", ["subject", "object"]),
            
            # "X follows Y" -> follows(?x, ?y)
            f"{entity_pattern}\\s+follows?\\s+{entity_pattern}": ("follows", ["subject", "object"]),
            
            # "X has property Y" -> hasProperty(?x, ?y)
            f"{entity_pattern}\\s+has\\s+property\\s+(\\w+)": ("hasProperty", ["subject", "value"]),
            
            # "X has attitude toward Y" -> hasAttitudeToward(?x, ?y)
            f"{entity_pattern}\\s+has\\s+attitude\\s+toward\\s+{entity_pattern}": ("hasAttitudeToward", ["subject", "object"]),
            
            # "X holds Y" -> holds(?x, ?y)
            f"{entity_pattern}\\s+holds\\s+{entity_pattern}": ("holds", ["subject", "object"]),
            
            # "X is different from Y" -> differentFrom(?x, ?y) - MUST come before general "is" pattern
            f"{entity_pattern}\\s+is\\s+different\\s+from\\s+{entity_pattern}": ("differentFrom", ["subject", "object"]),
            
            # "X is Y" (class membership) -> Y(?x)
            r"(\?\w+)\s+is\s+a?\s*(\w+)": ("class", ["instance", "class"]),
        }
        
        # Variable patterns
        self.var_pattern = re.compile(r'\?(\w+)')
        
    def parse_rule(self, condition: str, consequence: str, confidence: float = 1.0) -> ParsedRule:
        """Parse natural language rule into SWRL atoms"""
        
        # Extract variables from the rule
        variables = self._extract_variables(condition + " " + consequence)
        
        # Parse antecedent (condition)
        antecedent = self._parse_expression(condition, variables)
        
        # Parse consequent (consequence)
        consequent = self._parse_expression(consequence, variables)
        
        return ParsedRule(
            antecedent=antecedent,
            consequent=consequent,
            variables=variables,
            confidence=confidence
        )
    
    def _extract_variables(self, text: str) -> Set[str]:
        """Extract SWRL variables from text"""
        
        variables = set()
        
        # Look for ?variable notation
        for match in self.var_pattern.finditer(text):
            variables.add(f"?{match.group(1)}")
            
        # Also look for implicit variables (Person X -> ?x)
        implicit_pattern = r'\b(Person|Agent|Group|Entity)\s+([A-Z]\w*)\b'
        for match in re.finditer(implicit_pattern, text):
            var_name = match.group(2).lower()
            variables.add(f"?{var_name}")
            
        return variables
    
    def _parse_expression(self, expr: str, variables: Set[str]) -> List[SWRLAtom]:
        """Parse a logical expression into SWRL atoms"""
        
        atoms = []
        
        # Split by AND/OR connectives
        parts = re.split(r'\s+AND\s+|\s+and\s+', expr)
        
        for part in parts:
            part = part.strip()
            
            
            # Try to match against known patterns
            atom = self._match_pattern(part, variables)
            if atom:
                atoms.append(atom)
            else:
                # Fallback: try to parse as generic predicate
                atom = self._parse_generic(part, variables)
                if atom:
                    atoms.append(atom)
                else:
                    logger.warning(f"Could not parse expression part: {part}")
        
        return atoms
    
    def _match_pattern(self, text: str, variables: Set[str]) -> Optional[SWRLAtom]:
        """Match text against known patterns"""
        
        # Normalize text
        text = text.strip()
        
        # First, try to match the pattern as-is to capture groups
        for pattern, (predicate_template, arg_types) in self.patterns.items():
            # Create a version of the pattern that captures variables
            var_pattern = pattern
            
            # Replace (\w+) with a pattern that matches variables or entities
            var_pattern = var_pattern.replace(r'(\w+)', r'((?:\?\w+|\w+))')
            
            match = re.match(var_pattern, text, re.IGNORECASE)
            if match and predicate_template == "differentFrom":
                logger.info(f"Matched differentFrom pattern: text='{text}', groups={match.groups()}")
            if match:
                groups = match.groups()
                
                if predicate_template == "class":
                    # Special handling for class membership
                    instance = groups[0]
                    class_name = groups[1].capitalize()
                    return SWRLAtom(
                        atom_type=AtomType.CLASS,
                        predicate=class_name,
                        arguments=[instance]
                    )
                elif predicate_template == "differentFrom":
                    # differentFrom is a builtin in SWRL
                    arguments = list(groups)
                    logger.info(f"Creating differentFrom atom with arguments: {arguments}")
                    return SWRLAtom(
                        atom_type=AtomType.BUILTIN,
                        predicate="differentFrom",
                        arguments=arguments
                    )
                else:
                    # Property assertion
                    arguments = list(groups)
                    return SWRLAtom(
                        atom_type=AtomType.OBJECT_PROPERTY,
                        predicate=predicate_template,
                        arguments=arguments
                    )
        
        return None
    
    def _parse_generic(self, text: str, variables: Set[str]) -> Optional[SWRLAtom]:
        """Parse generic predicate structure: predicate(arg1, arg2, ...)"""
        
        # Match predicate(args) pattern
        match = re.match(r'(\w+)\s*\((.*?)\)', text)
        if match:
            predicate = match.group(1)
            args_str = match.group(2)
            arguments = [arg.strip() for arg in args_str.split(',')]
            
            # Determine atom type based on predicate name
            atom_type = AtomType.OBJECT_PROPERTY  # Default
            
            return SWRLAtom(
                atom_type=atom_type,
                predicate=predicate,
                arguments=arguments
            )
        
        return None
    
    def rule_to_swrl_string(self, rule: ParsedRule) -> str:
        """Convert parsed rule to SWRL syntax string"""
        
        antecedent_str = " ^ ".join(atom.to_swrl() for atom in rule.antecedent)
        consequent_str = " ^ ".join(atom.to_swrl() for atom in rule.consequent)
        
        return f"{antecedent_str} -> {consequent_str}"


# Example usage
if __name__ == "__main__":
    parser = SWRLParser()
    
    # Test cases
    test_rules = [
        {
            "condition": "Person ?x belongs to Group ?g AND Person ?y belongs to Group ?g",
            "consequence": "Person ?x shows bias toward Person ?y"
        },
        {
            "condition": "Agent ?a has property leadership AND Agent ?a belongs to Group ?g",
            "consequence": "Agent ?a influences Group ?g"
        },
        {
            "condition": "?x is a Student and ?x belongs to ?university",
            "consequence": "?x has property affiliated"
        }
    ]
    
    for test in test_rules:
        rule = parser.parse_rule(test["condition"], test["consequence"])
        swrl_string = parser.rule_to_swrl_string(rule)
        print(f"\nOriginal:")
        print(f"  Condition: {test['condition']}")
        print(f"  Consequence: {test['consequence']}")
        print(f"SWRL: {swrl_string}")
        print(f"Variables: {rule.variables}")