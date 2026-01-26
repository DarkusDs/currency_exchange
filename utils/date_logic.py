from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationError


class YYYYMMDDDate(BaseModel):
    """
    Pydantic model that validates a date string strictly in YYYYMMDD format
    """
    date: str

    @field_validator('date')
    @classmethod
    def validate_yyyymmdd(cls, value: str) -> str:
        """
        Validates that the provided string represents a real date in YYYYMMDD format

        :param value: Date string to validate
        :return: Validated date string if the format and value are correct
        """
        if not value.isdigit() or len(value) != 8:
            raise ValueError("Дата має бути у форматі YYYYMMDD")

        try:
            datetime.strptime(value, '%Y%m%d')
            return value
        except ValueError:
            raise ValueError("Невірна дата")


def validate_date(date_str: str) -> bool:
    """
    Function for backward compatibility, working with pydantic model

    :param date_str: Date string to validate
    :return: True if the date is valid, otherwise False
    """
    try:
        YYYYMMDDDate(date=date_str)
        return True
    except ValidationError:
        return False


def get_validated_date(date_input: str | None) -> str:
    """
    Function returns validated date or current if date was None

    :param date_input: Optional date string to validate
    :return: Validated date string in YYYYMMDD format
    """
    if date_input is None:
        return datetime.today().strftime('%Y%m%d')

    YYYYMMDDDate(date=date_input)
    return date_input
