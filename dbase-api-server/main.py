"""Microservice main module."""

import os

import dotenv
import uvicorn
from fastapi import FastAPI

from dbase_api_server.containers import PostgresConnectionParams
from dbase_api_server.dbase import StorageDBase
from dbase_api_server.models import Deposit, Response, StationInfo, WorkInfo

dotenv.load_dotenv()

app = FastAPI()
dbase_adapter = StorageDBase(
    PostgresConnectionParams(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        dbname=os.getenv('POSTGRES_DB')
    )
)


@app.get('/ping')
def check_service_alive() -> dict:
    """Return ping-pong response.

    Returns: dict object with status and message

    """
    returning_info = Response(
        status=True,
        message='Service is alive',
        data={}
    )
    return returning_info.dict()


@app.get('/get-all-deposits')
def get_all_deposits() -> dict:
    """Return all deposits name from deposit table.

    Returns: dict object with operation status, message with
    operation discription and all deposit area names.
    """
    area_names = dbase_adapter.get_all_deposit_names()
    if area_names is None:
        area_names = []

    returning_info = Response(
        status=True,
        message='All deposits name returns successfully',
        data={
            'area_names': area_names
        }
    )
    return returning_info.dict()


@app.post('/add-deposit')
def add_new_deposit(deposit: Deposit) -> dict:
    """Add deposit info to database.

    Args:
        deposit: deposits area name

    Returns: dict object with request status, message with
    action discription and added deposit area name.
    """
    is_added = dbase_adapter.add_deposit_info(
        area_name=deposit.area_name
    )
    if is_added:
        message = f'Deposit name "{deposit.area_name}" added successfully'
    else:
        message = f'Cant add deposit name "{deposit.area_name}"'

    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info.dict()


@app.post('/update-deposit')
def update_deposit_info(old_deposit: Deposit, new_deposit: Deposit) -> dict:
    """Update deposit name.

    Args:
        old_deposit: deposit area name
        new_deposit: updated deposit area name

    Returns: dict object with request status, message with
    action discription and updated deposit area name.
    """
    is_added = dbase_adapter.update_deposit_name(
        old_area_name=old_deposit.area_name,
        new_area_name=new_deposit.area_name
    )
    if is_added:
        message = (
            f'Deposit "{old_deposit.area_name}" successfully '
            f'renamed to "{new_deposit.area_name}"'
        )
    else:
        message = (
            f'Cant rename "{old_deposit.area_name} to '
            f'"{new_deposit.area_name}"'
        )

    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info.dict()


@app.post('/add-work-info')
def add_work_info(work_info: WorkInfo) -> dict:
    """Add work info to database.

    Args:
        work_info: works fields (well_name, datetime_start_str,
        work_type, deposit_id)
    """
    is_added = dbase_adapter.add_work_info(work_info=work_info)
    if is_added:
        message = (
            f'Successfully added work info: {work_info.well_name}, '
            f'{work_info.datetime_start_str}, '
            f'{work_info.work_type}, {work_info.deposit_id}'
        )
    else:
        message = (
            f'Cant add work info: {work_info.well_name}, '
            f'{work_info.datetime_start_str}, '
            f'{work_info.work_type}, {work_info.deposit_id}'
        )

    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info.dict()


@app.post('/update-work-info')
def update_work_info(old_work_info: WorkInfo,
                     new_work_info: WorkInfo) -> dict:
    """Update work info in database.

    Args:
        old_work_info: works fields (well_name, datetime_start_str,
        work_type, deposit_id)
        new_work_info: updated works fields (well_name, datetime_start_str,
        work_type, deposit_id)

    """
    is_added = dbase_adapter.update_work_info(
        old_work_info=old_work_info,
        new_work_info=new_work_info
    )
    if is_added:
        message = (
            f'Work info "{old_work_info.well_name}", '
            f'"{old_work_info.datetime_start_str}", '
            f'"{old_work_info.work_type}","{old_work_info.deposit_id}" '
            f'successfully changed to "{new_work_info.well_name}", '
            f'"{new_work_info.datetime_start_str}", '
            f'"{new_work_info.work_type}", "{new_work_info.deposit_id}".'
        )
    else:
        message = (
            f'Cant change "{old_work_info.well_name}", '
            f'"{old_work_info.datetime_start_str}", '
            f'"{old_work_info.work_type}","{old_work_info.deposit_id}" '
            f'to "{new_work_info.well_name}", '
            f'"{new_work_info.datetime_start_str}", '
            f'"{new_work_info.work_type}", "{new_work_info.deposit_id}".'
        )
    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info.dict()


@app.post('/add-station-info')
def add_station_info(station_info: StationInfo) -> dict:
    """Add station info to database.

    Args:
        station_info: station fields (station_number, x_wgs84,
        y_wgs84, altitude, work_id)

    Returns: dict object with request status and message with
    action discription.
    """
    is_added = dbase_adapter.add_station_info(station_info=station_info)
    if is_added:
        message = (
            f'Successfully added station info: '
            f'{station_info.station_number}, {station_info.x_wgs84},'
            f'{station_info.y_wgs84}, {station_info.altitude}, '
            f'{station_info.work_id}'
        )
    else:
        message = (
            f'Cant add station info: '
            f'{station_info.station_number}, {station_info.x_wgs84},'
            f'{station_info.y_wgs84}, {station_info.altitude}, '
            f'{station_info.work_id}'
        )

    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info.dict()


@app.post('/update-station-info')
def update_station_info(old_station_info: StationInfo,
                        new_station_info: StationInfo) -> dict:
    """Update station info.

    Args:
        old_station_info: container with station columns
        new_station_info: container with updated station columns

    Returns: dict object with request status, message with
    action discription.
    """
    is_added = dbase_adapter.update_station_info(
        old_station_info=old_station_info,
        new_station_info=new_station_info
    )
    if is_added:
        message = (
            f'Successfully changed station info: '
            f'{old_station_info.station_number}, '
            f'{old_station_info.x_wgs84}, {old_station_info.y_wgs84}, '
            f'{old_station_info.altitude}, {old_station_info.work_id} '
            f'to {new_station_info.station_number}, '
            f'{new_station_info.x_wgs84}, {new_station_info.y_wgs84}, '
            f'{new_station_info.altitude}, {new_station_info.work_id}.'
        )
    else:
        message = (
            f'Cant change station info: '
            f'{old_station_info.station_number}, '
            f'{old_station_info.x_wgs84}, {old_station_info.y_wgs84}, '
            f'{old_station_info.altitude}, {old_station_info.work_id} '
            f'to {new_station_info.station_number}, '
            f'{new_station_info.x_wgs84}, {new_station_info.y_wgs84}, '
            f'{new_station_info.altitude}, {new_station_info.work_id}.'
        )
    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info.dict()


@app.get('/get-stations-info/{work_id}')
def get_stations_info(work_id: int) -> dict:
    """Return stations info from table.

    Returns: dict object with operation status, message with
    operation discription and stations related to work.
    """
    station_info = dbase_adapter.get_stations_info(work_id)

    returning_info = Response(
        status=True,
        message=f'All works related to work with id:"{work_id}" '
                f'returend successfully',
        data={
            'work_info': station_info
        }
    )
    return returning_info.dict()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host=os.getenv('APP_HOST'),
        port=int(os.getenv('APP_PORT'))
    )
