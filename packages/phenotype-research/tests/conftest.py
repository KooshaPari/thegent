import pytest
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
sys.path.insert(0, src_path)
