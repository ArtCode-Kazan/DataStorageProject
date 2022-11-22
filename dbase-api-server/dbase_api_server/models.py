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
        datetime_start_str: time of works starting
        work_type: type of works
        deposit_id: id of deposit associated with well

    """
    well_name: str
    datetime_start_str: str
    work_type: str
    deposit_id: int


class StationInfo(BaseModel):
    """Model with parameters for acting with stations table.

    Args:
        station_number: number of station
        x_wgs84: x-coordinate
        y_wgs84: y - coordinate
        altitude: z - coordinate
        work_id: id of work associated with station

    """
    station_number: int
    x_wgs84: float
    y_wgs84: float
    altitude: float
    work_id: int
