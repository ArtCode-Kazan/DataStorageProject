"""Module with class-models.

This module contains models with database fields.

"""

from typing import Union

from pydantic import BaseModel

DEFAULT_STRING = 'default_string'


class Response(BaseModel):
    """Model with API response params.

    Args:
        status: response status
        message: description with response action
        data: info about deposit area name

    """
    status: bool
    message: str
    data: Union[dict, list, int, float, str]


class Deposit(BaseModel):
    """Model with field for adding new deposit.

    Args:
        area_name: deposit name for adding

    """
    area_name: str
