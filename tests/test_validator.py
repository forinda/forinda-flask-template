"""
Tests for validator library.
"""

import pytest

from app.lib import Schema, ValidationError


class TestStringField:
    """Test string field validation."""

    def test_string_required(self):
        """Test required string field."""
        schema = Schema({'name': Schema.string().required()})

        with pytest.raises(ValidationError):
            schema.validate({})

    def test_string_min_length(self):
        """Test minimum string length."""
        schema = Schema({'name': Schema.string().min(3).required()})

        with pytest.raises(ValidationError):
            schema.validate({'name': 'ab'})

        result = schema.validate({'name': 'abc'})
        assert result['name'] == 'abc'

    def test_string_max_length(self):
        """Test maximum string length."""
        schema = Schema({'name': Schema.string().max(5).required()})

        with pytest.raises(ValidationError):
            schema.validate({'name': 'abcdef'})

        result = schema.validate({'name': 'abc'})
        assert result['name'] == 'abc'

    def test_email_validation(self):
        """Test email validation."""
        schema = Schema({'email': Schema.string().email().required()})

        # Valid email
        result = schema.validate({'email': 'test@example.com'})
        assert result['email'] == 'test@example.com'

        # Invalid email
        with pytest.raises(ValidationError) as exc:
            schema.validate({'email': 'not-an-email'})
        assert 'email' in str(exc.value).lower()

    def test_pattern_validation(self):
        """Test regex pattern validation."""
        schema = Schema({'slug': Schema.string().pattern(r'^[a-z0-9-]+$').required()})

        # Valid slug
        result = schema.validate({'slug': 'my-test-slug'})
        assert result['slug'] == 'my-test-slug'

        # Invalid slug
        with pytest.raises(ValidationError):
            schema.validate({'slug': 'My Invalid Slug!'})

    def test_string_trim(self):
        """Test string trimming."""
        schema = Schema({'name': Schema.string().trim().required()})

        result = schema.validate({'name': '  test  '})
        assert result['name'] == 'test'

    def test_string_transform(self):
        """Test string transformation."""
        schema = Schema({'email': Schema.string().transform(str.lower).required()})

        result = schema.validate({'email': 'Test@EXAMPLE.COM'})
        assert result['email'] == 'test@example.com'


class TestNumberField:
    """Test number field validation."""

    def test_number_int(self):
        """Test integer conversion."""
        schema = Schema({'age': Schema.number().int().required()})

        result = schema.validate({'age': '25'})
        assert result['age'] == 25
        assert isinstance(result['age'], int)

    def test_number_min(self):
        """Test minimum value."""
        schema = Schema({'age': Schema.number().int().min(18).required()})

        with pytest.raises(ValidationError):
            schema.validate({'age': 17})

        result = schema.validate({'age': 18})
        assert result['age'] == 18

    def test_number_max(self):
        """Test maximum value."""
        schema = Schema({'score': Schema.number().int().max(100).required()})

        with pytest.raises(ValidationError):
            schema.validate({'score': 101})

        result = schema.validate({'score': 100})
        assert result['score'] == 100


class TestBooleanField:
    """Test boolean field validation."""

    def test_boolean_conversion(self):
        """Test boolean conversion from various types."""
        schema = Schema({'active': Schema.boolean().required()})

        # From boolean
        assert schema.validate({'active': True})['active'] is True

        # From string
        assert schema.validate({'active': 'true'})['active'] is True
        assert schema.validate({'active': 'false'})['active'] is False

        # From number
        assert schema.validate({'active': 1})['active'] is True
        assert schema.validate({'active': 0})['active'] is False


class TestEnumField:
    """Test enum field validation."""

    def test_enum_validation(self):
        """Test enum value validation."""
        schema = Schema({'role': Schema.enum(['admin', 'user', 'guest']).required()})

        # Valid value
        result = schema.validate({'role': 'admin'})
        assert result['role'] == 'admin'

        # Invalid value
        with pytest.raises(ValidationError):
            schema.validate({'role': 'superadmin'})

    def test_enum_default(self):
        """Test enum with default value."""
        schema = Schema({'role': Schema.enum(['admin', 'user']).default('user')})

        result = schema.validate({})
        assert result['role'] == 'user'


class TestArrayField:
    """Test array field validation."""

    def test_array_validation(self):
        """Test basic array validation."""
        schema = Schema({'tags': Schema.array().required()})

        result = schema.validate({'tags': ['a', 'b', 'c']})
        assert result['tags'] == ['a', 'b', 'c']

    def test_array_min_length(self):
        """Test array minimum length."""
        schema = Schema({'tags': Schema.array().min(2).required()})

        with pytest.raises(ValidationError):
            schema.validate({'tags': ['a']})

        result = schema.validate({'tags': ['a', 'b']})
        assert len(result['tags']) == 2

    def test_array_with_items(self):
        """Test array with item validation."""
        schema = Schema({'emails': Schema.array(Schema.string().email()).required()})

        # Valid emails
        result = schema.validate({'emails': ['test1@example.com', 'test2@example.com']})
        assert len(result['emails']) == 2

        # Invalid email in array
        with pytest.raises(ValidationError):
            schema.validate({'emails': ['valid@example.com', 'invalid']})


class TestObjectField:
    """Test nested object validation."""

    def test_nested_object(self):
        """Test nested object validation."""
        schema = Schema(
            {
                'user': Schema.object(
                    {'name': Schema.string().required(), 'email': Schema.string().email().required()}
                ).required()
            }
        )

        result = schema.validate({'user': {'name': 'John', 'email': 'john@example.com'}})

        assert result['user']['name'] == 'John'
        assert result['user']['email'] == 'john@example.com'

    def test_nested_object_validation_error(self):
        """Test nested object validation errors."""
        schema = Schema({'user': Schema.object({'email': Schema.string().email().required()}).required()})

        with pytest.raises(ValidationError):
            schema.validate({'user': {'email': 'invalid'}})


class TestOptionalAndDefaults:
    """Test optional fields and default values."""

    def test_optional_field(self):
        """Test optional field."""
        schema = Schema({'name': Schema.string().required(), 'bio': Schema.string().optional()})

        result = schema.validate({'name': 'John'})
        assert result['name'] == 'John'
        assert result['bio'] is None

    def test_default_value(self):
        """Test default value."""
        schema = Schema({'name': Schema.string().required(), 'role': Schema.string().default('user')})

        result = schema.validate({'name': 'John'})
        assert result['role'] == 'user'


class TestCustomValidators:
    """Test custom validator functions."""

    def test_custom_validator(self):
        """Test custom validation function."""

        def is_even(x):
            return int(x) % 2 == 0

        schema = Schema({'number': Schema.number().int().custom(is_even, 'Number must be even').required()})

        # Valid
        result = schema.validate({'number': 4})
        assert result['number'] == 4

        # Invalid
        with pytest.raises(ValidationError) as exc:
            schema.validate({'number': 3})
        assert 'even' in str(exc.value).lower()


class TestSafeValidate:
    """Test safe_validate method."""

    def test_safe_validate_success(self):
        """Test safe_validate with valid data."""
        schema = Schema({'name': Schema.string().required()})

        success, result = schema.safe_validate({'name': 'John'})

        assert success is True
        assert result['name'] == 'John'

    def test_safe_validate_failure(self):
        """Test safe_validate with invalid data."""
        schema = Schema({'email': Schema.string().email().required()})

        success, errors = schema.safe_validate({'email': 'invalid'})

        assert success is False
        assert len(errors) > 0
