import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcm_repairer.main import repair_model

def main():
    file_path = os.path.join(os.path.dirname(__file__), 'model.stl')
    result = repair_model(file_path)
    print(result)

if __name__ == "__main__":
    main()
