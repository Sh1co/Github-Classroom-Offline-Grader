def test_ci():
    # Read main.yaml
    with open('.github/workflows/main.yaml', 'r') as file:
        data = file.read()

    # Check if it contains 'pytest'
    assert 'pytest' in data, "The pytest is not included"
