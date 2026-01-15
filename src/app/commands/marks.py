"""
Marks command module for FIB Manager.

This module handles formula evaluation and variable solving for marks calculations.
It implements various mathematical formula utilities for academic mark calculations.
"""

import re
import json
import argparse
import logging
import sys
from argparse import Namespace
from typing import Dict, List, Set, Tuple, Any, Optional, Union, Callable

from app.ui.ui import display_marks_results, check_windows_interactive

# Configure logger
logger = logging.getLogger(__name__)

# Define a list of allowed mathematical functions for safe evaluation
ALLOWED_FUNCTIONS = ['min', 'max', 'round', 'abs', 'sum', 'pow']
TOLERANCE = 1e-6
MAX_ITERATIONS = 10


def add_marks_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add arguments for the marks command.
    
    Args:
        parser: ArgumentParser object
    """
    parser.add_argument("--formula", type=str, required=False,
                        help="Mathematical formula with variable names (use quotes to escape special characters)")
    parser.add_argument("--target", type=float, required=False,
                        help="Target result value for the formula")
    parser.add_argument("--values", type=str, nargs="+", required=False,
                        help="Known variable values in format VAR=VALUE")
    parser.add_argument("-v", "--view", action="store_true",
                        help="Display results in an interactive table view")


def handle_marks_command(args: Namespace) -> None:
    """
    Handle the marks command by processing formula inputs and calculating results.
    
    Args:
        args: ArgumentParser arguments
    """
    try:
        if not args.formula or not args.target:
            print("Error: You must specify --formula and --target")
            return
            
        # Parse values from command line
        values = parse_variable_values(args.values or [])
        problem = {
            "formula": args.formula,
            "values": values,
            "target": float(args.target)
        }
        
        # Process the formula
        formula = problem["formula"]
        values = problem["values"]
        target = problem["target"]
        
        # Find the solution
        values, result, solution = process_marks_calculation(formula, values, target)
        
        # Format and output results
        if args.view:
            if not check_windows_interactive():
                return
            display_marks_results(formula, values, target, solution, result)
        else:
            results = format_results(formula, values, target, solution)
            print(json.dumps(results, indent=2))  # Always use pretty formatting
        
    except Exception as e:
        logger.error(f"Error processing formula: {str(e)}")
        print(f"Error: {str(e)}")


def parse_variable_values(value_strings: List[str]) -> Dict[str, float]:
    """
    Parse variable values from command line strings in the format VAR=VALUE.
    
    Args:
        value_strings: List of strings in the format "VAR=VALUE"
        
    Returns:
        Dictionary mapping variable names to their numeric values
        
    Raises:
        ValueError: If a value string is not in the correct format
    """
    values = {}
    for val_str in value_strings:
        if "=" not in val_str:
            raise ValueError(f"Invalid value format: {val_str}. Expected VAR=VALUE")
        
        var, val = val_str.split("=", 1)
        try:
            values[var.strip()] = float(val.strip())
        except ValueError:
            raise ValueError(f"Invalid numeric value for {var}: {val}")
    
    return values


def find_variable_names(formula: str) -> List[str]:
    """
    Extract and return sorted unique variable names from a formula.
    
    Args:
        formula: Mathematical expression with variable names
        
    Returns:
        Sorted list of unique variable names
    """
    potential_variables = re.findall(r'\b[A-Za-z][A-Za-z0-9]*\b', formula)
    actual_variables = [var for var in potential_variables if var not in ALLOWED_FUNCTIONS]
    return sorted(set(actual_variables))


def get_missing_variables(formula: str, provided_values: Dict[str, float]) -> List[str]:
    """
    Identify variables in the formula that have no provided values.
    
    Args:
        formula: Mathematical expression
        provided_values: Dictionary with known variable values
        
    Returns:
        List of variable names that are missing values
    """
    variables_in_formula = find_variable_names(formula)
    return [var for var in variables_in_formula if var not in provided_values]


def replace_comparison_operators(formula: str) -> str:
    """
    Convert comparison expressions to return 1.0 or 0.0 instead of True/False.
    
    Args:
        formula: The mathematical formula
        
    Returns:
        Modified formula with wrapped comparison expressions
    """
    comp_pattern = r'(\([^()]*[<>=!][=]?[^()]*\))'
    
    def convert_to_float(match):
        comp_expr = match.group(1)
        return f"float({comp_expr})"
        
    return re.sub(comp_pattern, convert_to_float, formula)


def prepare_formula_for_evaluation(formula: str, variable_values: Dict[str, float]) -> str:
    """
    Replace variables with values and prepare formula for evaluation.
    
    Args:
        formula: The mathematical formula
        variable_values: Dictionary of variable values
        
    Returns:
        Formula ready for evaluation
    """
    prepared_formula = formula
    
    # Replace variables with their values
    for var in find_variable_names(formula):
        val = variable_values.get(var, 0)
        prepared_formula = re.sub(rf'\b{var}\b', str(val), prepared_formula)
    
    # Convert caret (^) to Python's exponentiation operator (**)
    prepared_formula = prepared_formula.replace('^', '**')
    
    # Handle comparison operations
    return replace_comparison_operators(prepared_formula)


def create_safe_evaluation_context() -> Dict[str, Any]:
    """
    Create a restricted evaluation context with only allowed functions.
    
    Returns:
        Dictionary containing the safe evaluation context
    """
    allowed_builtins = {
        'min': min, 
        'max': max, 
        'abs': abs, 
        'round': round, 
        'sum': sum,
        'float': float,
        'pow': pow
    }
    
    return {'__builtins__': allowed_builtins}


def evaluate_formula(formula: str, values: Dict[str, float]) -> float:
    """
    Evaluate formula with the given variable values.
    
    Args:
        formula: Mathematical expression
        values: Dictionary of variable values
        
    Returns:
        Result of evaluating the formula
        
    Raises:
        ValueError: If the formula is invalid or contains disallowed functions
    """
    prepared_formula = prepare_formula_for_evaluation(formula, values)
    safe_context = create_safe_evaluation_context()
    
    try:
        return eval(prepared_formula, safe_context)
    except Exception as e:
        raise ValueError(f"Invalid formula or values: {e}")


def calculate_baseline_result(formula: str, values: Dict[str, float], missing_vars: List[str]) -> float:
    """
    Calculate formula result with all missing variables set to zero.
    
    Args:
        formula: Mathematical expression
        values: Dictionary of known variable values
        missing_vars: List of variables without values
        
    Returns:
        Result with missing variables set to zero
    """
    complete_values = values.copy()
    for var in missing_vars:
        complete_values[var] = 0.0
    return evaluate_formula(formula, complete_values)


def calculate_variable_impacts(formula: str, missing_vars: List[str]) -> Dict[str, float]:
    """
    Calculate how much each missing variable affects the formula output per unit.
    
    Args:
        formula: Mathematical expression
        missing_vars: List of variables without values
        
    Returns:
        Dictionary of variable names and their impact coefficients
    """
    coefficients = {}
    base_result = evaluate_formula(formula, {})  # All zeros
    
    for var in missing_vars:
        # Set only the current variable to 1, others to 0
        var_values = {var: 1.0}
        var_result = evaluate_formula(formula, var_values)
        coefficients[var] = var_result - base_result
        
    return coefficients


def create_default_solution(missing_vars: List[str], is_at_target: bool) -> Dict[str, float]:
    """
    Create a default solution when variables have no impact on formula result.
    
    Args:
        missing_vars: List of variables without values
        is_at_target: Whether current value already matches target
        
    Returns:
        Solution dictionary with arbitrary values
    """
    default_value = 0.0 if is_at_target else 1.0
    return {var: default_value for var in missing_vars}


def verify_solution(formula: str, values: Dict[str, float], solution: Dict[str, float]) -> float:
    """
    Verify the solution by evaluating the formula with all values filled in.
    
    Args:
        formula: Mathematical expression
        values: Dictionary of known variable values
        solution: Dictionary of calculated missing variable values
        
    Returns:
        Result of evaluating the formula with all values
    """
    complete_values = values.copy()
    complete_values.update(solution)
    return evaluate_formula(formula, complete_values)


def refine_solution(formula: str, values: Dict[str, float], 
                   initial_solution: Dict[str, float], 
                   target: float, baseline: float) -> Dict[str, float]:
    """
    Refine the initial solution iteratively for better accuracy.
    
    Args:
        formula: Mathematical expression
        values: Dictionary of known variable values
        initial_solution: First approximation of missing variable values
        target: Desired formula result
        baseline: Value with missing variables at zero
        
    Returns:
        Refined solution dictionary
    """
    solution = initial_solution.copy()
    
    for _ in range(MAX_ITERATIONS):
        current_result = verify_solution(formula, values, solution)
        current_gap = target - current_result
        
        # If we're close enough to target, stop iterating
        if abs(current_gap) < TOLERANCE:
            break
            
        # Calculate adjustment factor
        target_baseline_diff = target - baseline
        if abs(target_baseline_diff) < TOLERANCE:
            adjustment_factor = 1.0
        else:
            adjustment_factor = current_gap / target_baseline_diff
            
        # Adjust each variable proportionally to close the gap
        for var in solution:
            solution[var] = solution[var] * (1 + adjustment_factor * 0.5)
    
    return solution


def create_initial_solution(missing_vars: List[str], target_gap: float, 
                           variable_impacts: Dict[str, float]) -> Dict[str, float]:
    """
    Create an initial solution for missing variables.
    
    Args:
        missing_vars: List of variables without values
        target_gap: The gap between current and target value
        variable_impacts: Dictionary of variable impact coefficients
        
    Returns:
        Initial solution dictionary
    """
    solution = {}
    
    # Handle single variable case
    if len(missing_vars) == 1:
        var = missing_vars[0]
        if variable_impacts[var] != 0:
            solution[var] = target_gap / variable_impacts[var]
        else:
            solution[var] = 0.0
        return solution
        
    # Handle multiple variables case
    total_impact = sum(variable_impacts.values())
    distribution_factor = target_gap / total_impact if abs(total_impact) > TOLERANCE else 0.0
    
    for var in missing_vars:
        if variable_impacts[var] != 0:
            solution[var] = distribution_factor
        else:
            solution[var] = 0.0
            
    return solution


def solve_for_missing_variables(formula: str, values: Dict[str, float], target: float) -> Dict[str, float]:
    """
    Solve for all missing variables to reach the target value.
    If multiple variables are missing, distribute the value among them.
    
    Args:
        formula: Mathematical expression
        values: Dictionary of known variable values
        target: Desired formula result
        
    Returns:
        Dictionary with values for missing variables
    """
    missing_vars = get_missing_variables(formula, values)
    
    if not missing_vars:
        return {}
        
    baseline = calculate_baseline_result(formula, values, missing_vars)
    variable_impacts = calculate_variable_impacts(formula, missing_vars)
    
    # Calculate the total contribution needed from missing variables
    target_gap = target - baseline
    total_impact = sum(variable_impacts.values())
    
    # Handle the case where variables have no impact
    if abs(total_impact) < TOLERANCE:
        is_at_target = abs(baseline - target) < TOLERANCE
        solution = create_default_solution(missing_vars, is_at_target)
        actual_result = verify_solution(formula, values, solution)
        logger.warning(f"Variables have no effect. Target {target} cannot be reached. Best result: {actual_result}")
        return solution
    
    # Create and refine solution
    initial_solution = create_initial_solution(missing_vars, target_gap, variable_impacts)
    return refine_solution(formula, values, initial_solution, target, baseline)


def format_results(formula: str, values: Dict[str, float], target: float, solution: Dict[str, float]) -> Dict[str, Any]:
    """
    Format the results into a structured output.
    
    Args:
        formula: Mathematical expression
        values: Dictionary of known variable values
        target: Desired formula result
        solution: Dictionary of calculated missing variable values
        
    Returns:
        Formatted result dictionary
    """
    missing_vars = get_missing_variables(formula, values)
    baseline = calculate_baseline_result(formula, values, missing_vars)
    
    return {
        "formula": formula,
        "values": values,
        "target": target,
        "result": round(baseline, 2),
        "solution": {var: round(val, 2) for var, val in solution.items()}
    }


def process_marks_calculation(formula: str, 
                           values: Dict[str, float], 
                           target: float) -> Tuple[Dict[str, float], float, Dict[str, float]]:
    """
    Process a marks calculation request.
    
    This is a utility function that centralizes the calculation logic for both
    the CLI and interactive interfaces, following the DRY principle.
    
    Args:
        formula: Mathematical expression
        values: Dictionary of known variable values
        target: Target result value
        
    Returns:
        Tuple of (values, result, solution)
    """
    # Find missing variables
    missing_vars = get_missing_variables(formula, values)
    
    # Calculate current result with known values
    result = calculate_baseline_result(formula, values, missing_vars)
    
    # Calculate solution
    solution = solve_for_missing_variables(formula, values, target)
    
    return values, result, solution
