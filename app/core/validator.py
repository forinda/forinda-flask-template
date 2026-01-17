"""
Zod-like schema validation for Python.

Example usage:
    from app.lib.validator import Schema, ValidationError

    # Define schema
    user_schema = Schema({
        'email': Schema.string().email().required(),
        'name': Schema.string().min(2).max(50).required(),
        'age': Schema.number().min(18).optional(),
        'role': Schema.enum(['admin', 'user', 'guest']).default('user')
    })

    # Validate data
    try:
        validated = user_schema.validate(data)
        # Use validated data
    except ValidationError as e:
        # Handle validation errors
        print(e.errors)
"""

import re
from collections.abc import Callable
from typing import Any, Union

NumberUnion = Union[int, float]  # noqa: UP007


class ValidationError(Exception):
    """Exception raised when validation fails."""

    def __init__(self, errors: str | list[dict[str, Any]]):
        if isinstance(errors, str):
            self.errors = [{'field': 'root', 'message': errors}]
        else:
            self.errors = errors
        super().__init__(self._format_errors())

    def _format_errors(self) -> str:
        """Format errors for display."""
        if len(self.errors) == 1:
            return self.errors[0]['message']
        return '\n'.join([f'{e.get("field", "unknown")}: {e["message"]}' for e in self.errors])


class Field:
    """Base field validator."""

    def __init__(self, field_type: str):
        self.field_type = field_type
        self._required = False
        self._optional = False
        self._default = None
        self._has_default = False
        self._validators: list[Callable] = []
        self._transform: Callable | None = None

    def required(self, message: str = 'This field is required'):
        """Mark field as required."""
        self._required = True
        self._optional = False
        self._required_message = message
        return self

    def optional(self):
        """Mark field as optional."""
        self._optional = True
        self._required = False
        return self

    def default(self, value: Any):
        """Set default value."""
        self._default = value
        self._has_default = True
        self._optional = True
        return self

    def transform(self, func: Callable):
        """Transform value after validation."""
        self._transform = func
        return self

    def custom(self, validator: Callable[[Any], bool], message: str = 'Validation failed'):
        """Add custom validator function."""

        def validate(value):
            if not validator(value):
                raise ValidationError([{'field': 'root', 'message': message}])
            return value

        self._validators.append(validate)
        return self

    def validate(self, value: Any, field_name: str = 'field') -> Any:
        """Validate the field value."""
        # Handle None/missing values
        if value is None or value == '':
            if self._required:
                raise ValidationError(
                    [{'field': field_name, 'message': getattr(self, '_required_message', 'This field is required')}]
                )
            if self._has_default:
                return self._default
            if self._optional:
                return None
            raise ValidationError([{'field': field_name, 'message': 'This field is required'}])

        # Run all validators
        for validator in self._validators:
            try:
                value = validator(value)
            except ValidationError as e:
                # Re-raise with field name if not already set
                if isinstance(e.errors, list) and e.errors:
                    if e.errors[0].get('field') == 'root':
                        raise ValidationError([{'field': field_name, 'message': e.errors[0]['message']}])
                raise

        # Apply transform
        if self._transform:
            value = self._transform(value)

        return value


class StringField(Field):
    """String field validator."""

    def __init__(self):
        super().__init__('string')
        self._min_length = None
        self._max_length = None
        self._pattern = None

    def min(self, length: int, message: str = None):
        """Set minimum length."""

        def validate(value):
            if not isinstance(value, str):
                raise ValidationError(
                    [{'field': 'root', 'message': message or f'Expected string, got {type(value).__name__}'}]
                )
            if len(value) < length:
                raise ValidationError(
                    [{'field': 'root', 'message': message or f'String must be at least {length} characters'}]
                )
            return value

        self._validators.append(validate)
        return self

    def max(self, length: int, message: str = None):
        """Set maximum length."""

        def validate(value):
            if not isinstance(value, str):
                raise ValidationError(
                    [{'field': 'root', 'message': message or f'Expected string, got {type(value).__name__}'}]
                )
            if len(value) > length:
                raise ValidationError(
                    [{'field': 'root', 'message': message or f'String must be at most {length} characters'}]
                )
            return value

        self._validators.append(validate)
        return self

    def email(self, message: str = 'Invalid email address'):
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        def validate(value):
            if not isinstance(value, str) or not re.match(email_pattern, value):
                raise ValidationError([{'field': 'root', 'message': message}])
            return value

        self._validators.append(validate)
        return self

    def url(self, message: str = 'Invalid URL'):
        """Validate URL format."""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'

        def validate(value):
            if not isinstance(value, str) or not re.match(url_pattern, value):
                raise ValidationError([{'field': 'root', 'message': message}])
            return value

        self._validators.append(validate)
        return self

    def pattern(self, regex: str, message: str = 'Invalid format'):
        """Validate against regex pattern."""

        def validate(value):
            if not isinstance(value, str) or not re.match(regex, value):
                raise ValidationError([{'field': 'root', 'message': message}])
            return value

        self._validators.append(validate)
        return self

    def alpha(self, message: str = 'String must contain only letters'):
        """Validate alphabetic characters only."""
        return self.pattern(r'^[a-zA-Z]+$', message)

    def alphanumeric(self, message: str = 'String must contain only letters and numbers'):
        """Validate alphanumeric characters only."""
        return self.pattern(r'^[a-zA-Z0-9]+$', message)

    def lowercase(self, message: str = 'String must be lowercase'):
        """Validate lowercase string."""

        def validate(value):
            if not isinstance(value, str) or value != value.lower():
                raise ValidationError(message)
            return value

        self._validators.append(validate)
        return self

    def uppercase(self, message: str = 'String must be uppercase'):
        """Validate uppercase string."""

        def validate(value):
            if not isinstance(value, str) or value != value.upper():
                raise ValidationError(message)
            return value

        self._validators.append(validate)
        return self

    def trim(self):
        """Trim whitespace."""
        return self.transform(lambda x: x.strip() if isinstance(x, str) else x)


class NumberField(Field):
    """Number field validator."""

    def __init__(self):
        super().__init__('number')
        self._is_int = False

    def int(self):
        """Validate as integer."""
        self._is_int = True

        def validate(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValidationError(f'Expected integer, got {type(value).__name__}')

        self._validators.append(validate)
        return self

    def min(self, minimum: NumberUnion, message: str = None):
        """Set minimum value."""

        def validate(value):
            num_value = float(value) if not self._is_int else int(value)
            if num_value < minimum:
                raise ValidationError(message or f'Number must be at least {minimum}')
            return value

        self._validators.append(validate)
        return self

    def max(self, maximum: NumberUnion, message: str = None):
        """Set maximum value."""

        def validate(value):
            num_value = float(value) if not self._is_int else int(value)
            if num_value > maximum:
                raise ValidationError(message or f'Number must be at most {maximum}')
            return value

        self._validators.append(validate)
        return self

    def positive(self, message: str = 'Number must be positive'):
        """Validate positive number."""
        return self.min(0.0001 if not self._is_int else 1, message)

    def negative(self, message: str = 'Number must be negative'):
        """Validate negative number."""
        return self.max(-0.0001 if not self._is_int else -1, message)


class BooleanField(Field):
    """Boolean field validator."""

    def __init__(self):
        super().__init__('boolean')

        def validate(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ('true', '1', 'yes', 'on'):
                    return True
                if value.lower() in ('false', '0', 'no', 'off'):
                    return False
            if isinstance(value, int):
                return bool(value)
            raise ValidationError(f'Expected boolean, got {type(value).__name__}')

        self._validators.append(validate)


class EnumField(Field):
    """Enum field validator."""

    def __init__(self, values: list[Any]):
        super().__init__('enum')
        self._values = values

        def validate(value):
            if value not in self._values:
                raise ValidationError(f'Value must be one of: {", ".join(map(str, self._values))}')
            return value

        self._validators.append(validate)


class ArrayField(Field):
    """Array field validator."""

    def __init__(self, item_schema: Field = None):
        super().__init__('array')
        self._item_schema = item_schema
        self._min_length = None
        self._max_length = None

    def min(self, length: int, message: str = None):
        """Set minimum array length."""

        def validate(value):
            if not isinstance(value, list):
                raise ValidationError(f'Expected array, got {type(value).__name__}')
            if len(value) < length:
                raise ValidationError(message or f'Array must have at least {length} items')
            return value

        self._validators.append(validate)
        return self

    def max(self, length: int, message: str = None):
        """Set maximum array length."""

        def validate(value):
            if not isinstance(value, list):
                raise ValidationError(f'Expected array, got {type(value).__name__}')
            if len(value) > length:
                raise ValidationError(message or f'Array must have at most {length} items')
            return value

        self._validators.append(validate)
        return self

    def validate(self, value: Any, field_name: str = 'field') -> Any:
        """Validate array and its items."""
        value = super().validate(value, field_name)

        if value is None:
            return value

        if not isinstance(value, list):
            raise ValidationError(f'{field_name}: Expected array, got {type(value).__name__}')

        # Validate each item if schema provided
        if self._item_schema:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_items.append(self._item_schema.validate(item, f'{field_name}[{i}]'))
                except ValidationError as e:
                    raise ValidationError(f'{field_name}[{i}]: {e!s}')
            return validated_items

        return value


class ObjectField(Field):
    """Object field validator."""

    def __init__(self, schema: dict[str, Field]):
        super().__init__('object')
        self._schema = schema

    def validate(self, value: Any, field_name: str = 'field') -> dict[str, Any]:
        """Validate object against schema."""
        if value is None:
            if self._required:
                raise ValidationError(f'{field_name}: This field is required')
            if self._has_default:
                return self._default
            if self._optional:
                return None
            raise ValidationError(f'{field_name}: This field is required')

        if not isinstance(value, dict):
            raise ValidationError(f'{field_name}: Expected object, got {type(value).__name__}')

        validated = {}
        errors = []

        for key, field_schema in self._schema.items():
            try:
                validated[key] = field_schema.validate(value.get(key), key)
            except ValidationError as e:
                errors.extend(e.errors)

        if errors:
            raise ValidationError(errors)

        return validated


class Schema:
    """Main schema validator."""

    def __init__(self, schema: dict[str, Field] = None):
        self._schema = schema or {}

    @staticmethod
    def string() -> StringField:
        """Create string field."""
        return StringField()

    @staticmethod
    def number() -> NumberField:
        """Create number field."""
        return NumberField()

    @staticmethod
    def boolean() -> BooleanField:
        """Create boolean field."""
        return BooleanField()

    @staticmethod
    def enum(values: list[Any]) -> EnumField:
        """Create enum field."""
        return EnumField(values)

    @staticmethod
    def array(item_schema: Field = None) -> ArrayField:
        """Create array field."""
        return ArrayField(item_schema)

    @staticmethod
    def object(schema: dict[str, Field]) -> ObjectField:
        """Create object field."""
        return ObjectField(schema)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate data against schema.

        Args:
            data: Data to validate

        Returns:
            Validated and transformed data

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError(f'Expected object, got {type(data).__name__}')

        validated = {}
        errors = []

        for key, field_schema in self._schema.items():
            try:
                validated[key] = field_schema.validate(data.get(key), key)
            except ValidationError as e:
                errors.extend(e.errors)

        if errors:
            raise ValidationError(errors)

        return validated

    def safe_validate(self, data: dict[str, Any]) -> tuple[bool, dict[str, Any] | list[dict[str, Any]]]:
        """
        Validate data and return success status with result or errors.

        Args:
            data: Data to validate

        Returns:
            Tuple of (success: bool, result or errors)
        """
        try:
            result = self.validate(data)
            return True, result
        except ValidationError as e:
            return False, e.errors
