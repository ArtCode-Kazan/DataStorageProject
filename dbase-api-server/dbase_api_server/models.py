"""Module with class-models.

This module contains models with database fields.

"""

from typing import Union

from pydantic import BaseModel

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


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


class WorkInfo(BaseModel):
    """Model with parameters for acting with works table.

    Args:
        name: well name
        datetime_start_str: time of works starting
        type: type of works
        deposit_id: id of deposit associated with well

    """
    name: str
    datetime_start_str: str
    type: str
    deposit_id: int
