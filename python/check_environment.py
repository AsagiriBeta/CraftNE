#!/usr/bin/env python3
"""
检查Python环境和依赖
"""
import sys
import subprocess
import json

def check_python_version():
    return sys.version_info >= (3, 8)

def check_dependencies():
    required_packages = [
        'torch',
        'torchvision', 
        'numpy',
        'pillow',
        'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def main():
    result = {
        'python_version': sys.version,
        'python_compatible': check_python_version(),
        'missing_packages': check_dependencies()
    }
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()