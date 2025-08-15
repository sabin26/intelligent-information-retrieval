import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from classifier import load_classifier_and_labels
__all__ = ['load_classifier_and_labels']
