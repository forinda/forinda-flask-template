# Flask API Tests

## Setup

Install test dependencies:
```bash
pipenv install --dev pytest pytest-cov pytest-flask
```

Or:
```bash
pip install -r requirements-test.txt
```

## Running Tests

### Run all tests
```bash
pipenv run pytest
```

### Run with coverage
```bash
pipenv run pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pipenv run pytest tests/test_auth.py
```

### Run specific test class
```bash
pipenv run pytest tests/test_auth.py::TestRegister
```

### Run specific test
```bash
pipenv run pytest tests/test_auth.py::TestRegister::test_register_success
```

### Run with verbose output
```bash
pipenv run pytest -v
```

### Run and stop on first failure
```bash
pipenv run pytest -x
```

## Test Structure

```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_validator.py     # Validator library tests
├── test_auth.py          # Authentication endpoint tests
└── test_categories.py    # Category endpoint tests
```

## Test Coverage

### Validator Tests
- ✅ String validation (min, max, email, pattern, trim, transform)
- ✅ Number validation (int, min, max, positive, negative)
- ✅ Boolean validation and conversion
- ✅ Enum validation and defaults
- ✅ Array validation with items
- ✅ Nested object validation
- ✅ Optional fields and defaults
- ✅ Custom validators
- ✅ Safe validate method

### Auth Tests
- ✅ User registration (success, duplicate email, invalid data)
- ✅ User login (success, invalid credentials)
- ✅ Protected endpoints (logout, profile)
- ✅ Password validation

### Category Tests
- ✅ Get categories with pagination
- ✅ Create category (success, duplicate slug, invalid slug)
- ✅ Update category
- ✅ Delete category
- ✅ Authentication requirements

## Writing New Tests

### Example Test
```python
def test_my_feature(client, clean_db):
    """Test my new feature."""
    response = client.post('/api/endpoint',
        data=json.dumps({'key': 'value'}),
        content_type='application/json',
        headers={'Authorization': 'Bearer mock_token'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'expected_key' in data
```

### Fixtures Available

- `app` - Flask app instance
- `client` - Test client for making requests
- `runner` - CLI test runner
- `clean_db` - Cleans test data before/after tests

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=app
```

## Test Database

Tests use the same MongoDB instance but with test data prefixes:
- Test emails: `test.*@example.com`
- Test slugs: `test-*`

The `clean_db` fixture automatically cleans up test data.

**Warning**: Do not run tests against production database!

## Mocking

Authentication is mocked in tests:
- Any request with `Authorization: Bearer mock_token` is considered authenticated
- User ID is mocked as `mock_user_id_123`

For production tests, implement proper JWT token generation.
