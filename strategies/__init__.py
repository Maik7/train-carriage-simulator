# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 15:16:04 2025

@author: mjustus
"""

"""
Strategies package - automatically collects all strategy modules.
"""
import os
import importlib
from typing import Dict, Callable

# Dictionary to hold all strategies
strategies: Dict[str, Callable] = {}

# Automatically import all .py files in this directory (except __init__.py)
package_dir = os.path.dirname(__file__)

for filename in os.listdir(package_dir):
    if filename.endswith('.py') and filename not in ['__init__.py', 'base_strategy.py']:
        module_name = filename[:-3]  # Remove .py extension
        
        try:
            # Import the module
            module = importlib.import_module(f'.{module_name}', package='strategies')
            
            # Look for strategy functions in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                # Check if it's a callable function (not a class or built-in)
                if callable(attr) and not attr_name.startswith('_'):
                    # Check if it has the right signature (lamp_state, memory) params
                    try:
                        import inspect
                        sig = inspect.signature(attr)
                        params = list(sig.parameters.keys())
                        if len(params) >= 2 and params[0] == 'lamp_state' and params[1] == 'memory':
                            # Use module name or function name as key
                            strategy_name = module_name.replace('_', '-').title()
                            strategies[strategy_name] = attr
                            print(f"Loaded strategy: {strategy_name} from {module_name}.py")
                    except:
                        pass
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")

# Alternative: Manual registration for more control
def register_strategy(name: str, strategy_func: Callable):
    """Manually register a strategy function."""
    strategies[name] = strategy_func

def get_strategy(name: str) -> Callable:
    """Get a strategy by name."""
    return strategies.get(name)

def list_strategies() -> list:
    """List all available strategies."""
    return list(strategies.keys())

# Export
__all__ = ['strategies', 'register_strategy', 'get_strategy', 'list_strategies']