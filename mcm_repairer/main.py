# mcm_repairer/main.py

def exported_method(a, b):
    """A simple method to add two numbers."""
    return a + b

def main():
    print("Running main function")
    result = exported_method(1, 2)
    print(f"1 + 2 = {result}")

if __name__ == "__main__":
    main()
