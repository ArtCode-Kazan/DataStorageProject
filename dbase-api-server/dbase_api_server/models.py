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
        well_name: well name
        work_start: time of works starting
        work_type: type of works
        deposit_id: id of deposit associated with well

    """
    well_name: str
    work_start: str
    work_type: str
    deposit_id: int
