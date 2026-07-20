
def add(a, b):
    return a + b

def test_add_one():
    assert add(2, 3) == 5

def test_add_two():
    assert add(0, 0) == 0

def test_add_three():
    assert add(-1, 1) == 0

if __name__ == "__main__":
    import subprocess
    with open("test_file.py", "w") as f:
        f.write(open(__file__).read())
    result = subprocess.run(["pytest", "test_file.py", "-v"], capture_output=True, text=True)
    print("PYTEST_EXIT_CODE:", result.returncode)
    print("PYTEST_STDOUT:", result.stdout)
