import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcm_repairer.main import exported_method

def main():
    result = exported_method(3, 4)
    print(f"3 + 4 = {result}")

if __name__ == "__main__":
    main()
