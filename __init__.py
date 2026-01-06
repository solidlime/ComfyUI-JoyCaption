import os
import importlib
import sys
from pathlib import Path
import logging

logger = logging.getLogger('ComfyUI.JoyCaption.Init')
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(name)s] %(levelname)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

current_dir = Path(__file__).parent

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

EXCLUDE_FILES = ['__init__.py', '__pycache__']

# Enable Windows color support
if sys.platform == 'win32':
    os.system('color')

# Check if llama-cpp-python is available for GGUF functionality
GGUF_AVAILABLE = False
try:
    import llama_cpp
    GGUF_AVAILABLE = True
except ImportError:
    # Use Windows color codes for better visibility
    logger.warning("="*80)
    logger.warning("llama-cpp-python library not found, GGUF functionality is not available")
    logger.warning("To use GGUF features, install additional dependencies:")
    logger.info("pip install -r requirements_gguf.txt")
    
    # Check if installation guide exists and provide link
    install_guide = current_dir / "llama_cpp_install.md"
    if install_guide.exists():
        logger.info(f"For detailed installation instructions with CUDA support, please see: {install_guide}")
    
    logger.info("Basic JoyCaption functionality is still available")
    logger.warning("="*80)
except Exception as e:
    logger.error(f"Error loading GGUF dependencies: {str(e)}")
    logger.info("Basic JoyCaption functionality is still available")

# Process all Python files in a deterministic order to avoid import-time races
for file in sorted(current_dir.glob('*.py')):
    if file.name not in EXCLUDE_FILES:
        try:
            module_name = file.stem
            spec = importlib.util.spec_from_file_location(module_name, str(file))
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # Skip GGUF module if llama-cpp-python is not available
            if not GGUF_AVAILABLE and module_name == 'JC_GGUF':
                continue
                
            spec.loader.exec_module(module)
            
            if hasattr(module, 'NODE_CLASS_MAPPINGS'):
                NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            
            if hasattr(module, 'NODE_DISPLAY_NAME_MAPPINGS'):
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {str(e)}")
            if module_name != 'JC_GGUF':  # Only show warning for non-GGUF modules
                logger.warning(f"Failed to load {module_name} module")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']