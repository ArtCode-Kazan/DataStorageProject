"""Microservice main module."""

import os

import dotenv
import uvicorn
from fastapi import FastAPI

from dbase_api_server.containers import PostgresConnectionParams
from dbase_api_server.dbase import StorageDBase
from dbase_api_server.models import (Deposit, Response, SeismicRecordInfo,
                                     StationInfo, WorkInfo)

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
def check_service_alive() -> Response:
    """Return ping-pong response.

    Returns: dict object with status and message

    """
    returning_info = Response(
        status=True,
        message='Service is alive',
        data={}
    )
    return returning_info


@app.get('/get-all-deposits')
def get_all_deposits() -> Response:
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
    return returning_info


@app.post('/add-deposit')
def add_new_deposit(deposit: Deposit) -> Response:
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
    return returning_info


@app.post('/update-deposit')
def update_deposit_info(old_deposit: Deposit,
                        new_deposit: Deposit) -> Response:
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
    return returning_info


@app.post('/add-work-info')
def add_work_info(work_info: WorkInfo) -> Response:
    """Add work info to database.

    Args:
        work_info: works fields (well_name, datetime_start_str,
        work_type, deposit_id)

    Returns: Response model object with request status, message with
    action discription.
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
    return returning_info


@app.post('/update-work-info')
def update_work_info(old_work_info: WorkInfo,
                     new_work_info: WorkInfo) -> Response:
    """Update work info in database.

    Args:
        old_work_info: works fields (well_name, datetime_start_str,
        work_type, deposit_id)
        new_work_info: updated works fields (well_name, datetime_start_str,
        work_type, deposit_id)

    Returns: Response model object with request status, message with
    action discription
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
    return returning_info


@app.get('/get-works-info/{deposit_id}')
def get_works_info(deposit_id: int) -> Response:
    """Return works info from works table.

    Args:
        deposit_id: id of deposit

    Returns: dict object with operation status, message with
    operation discription and works related to deposit.
    """
    works_info = dbase_adapter.get_works_info(deposit_id=deposit_id)

    returning_info = Response(
        status=True,
        message=f'All works related to deposit with id:{deposit_id} '
                f'returend successfully',
        data={
            'works_info': works_info
        }
    )
    return returning_info


@app.post('/add-station-info')
def add_station_info(station_info: StationInfo) -> Response:
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
            f'{station_info.station_number}, {station_info.x_wgs84}, '
            f'{station_info.y_wgs84}, {station_info.altitude}, '
            f'{station_info.work_id}'
        )
    else:
        message = (
            f'Cant add station info: '
            f'{station_info.station_number}, {station_info.x_wgs84}, '
            f'{station_info.y_wgs84}, {station_info.altitude}, '
            f'{station_info.work_id}'
        )

    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info


@app.post('/update-station-info')
def update_station_info(old_station_info: StationInfo,
                        new_station_info: StationInfo) -> Response:
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
    return returning_info


@app.get('/get-stations-info/{work_id}')
def get_stations_info(work_id: int) -> Response:
    """Return stations info from table.

    Args:
        work_id: associated with station work id

    Returns: dict object with operation status, message with
    operation discription and stations related to work.
    """
    stations_info = dbase_adapter.get_stations_info(
        work_id=work_id
    )

    returning_info = Response(
        status=True,
        message=f'All stations related to work with id:"{work_id}" '
                f'returend successfully',
        data={
            'stations_info': stations_info
        }
    )
    return returning_info


@app.post('/add-seimic-record-info')
def add_seismic_record(record_info: SeismicRecordInfo) -> Response:
    """Add seismic record info to database.

    Args:
        record_info: seismic record fields(station_id,
        datetime_start_str, datetime_stop_str, frequency,
        origin_name, unique_name, is_using)

    Returns: Response model object with request status, message with
    action discription.
    """
    is_added = dbase_adapter.add_seismic_record_info(record_info)
    if is_added:
        message = (
            f'Successfully added seismic record info: '
            f'{record_info.station_id}, '
            f'{record_info.datetime_start_str}, '
            f'{record_info.datetime_stop_str}, '
            f'{record_info.frequency}, {record_info.origin_name}, '
            f'{record_info.unique_name}, {record_info.is_using}'
        )
    else:
        message = (
            f'Cant add seismic record info: '
            f'{record_info.station_id}, '
            f'{record_info.datetime_start_str}, '
            f'{record_info.datetime_stop_str}, '
            f'{record_info.frequency}, {record_info.origin_name}, '
            f'{record_info.unique_name}, {record_info.is_using}'
        )

    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info


@app.post('/update-seismic-record-info')
def update_seismic_record_info(
    old_record_info: SeismicRecordInfo,
    new_record_info: SeismicRecordInfo
) -> Response:
    """Update seismic record info.

    Args:
        old_record_info: container with seismic record columns
        new_record_info: container with updated seismic record columns

    Returns: dict object with request status, message with
    action discription.
    """
    is_added = dbase_adapter.update_seismic_record_info(
        old_record_info=old_record_info,
        new_record_info=new_record_info
    )
    if is_added:
        message = (
            f'Successfully changed seismic record info '
            f'{old_record_info.station_id}, '
            f'{old_record_info.datetime_start_str}, '
            f'{old_record_info.datetime_stop_str}, '
            f'{old_record_info.frequency}, {old_record_info.origin_name}, '
            f'{old_record_info.unique_name}, {old_record_info.is_using} to '
            f'{new_record_info.station_id}, '
            f'{new_record_info.datetime_start_str}, '
            f'{new_record_info.datetime_stop_str}, '
            f'{new_record_info.frequency}, {new_record_info.origin_name}, '
            f'{new_record_info.unique_name}, {new_record_info.is_using}.'
        )
    else:
        message = (
            f'Cant change seismic record info '
            f'{old_record_info.station_id}, '
            f'{old_record_info.datetime_start_str}, '
            f'{old_record_info.datetime_stop_str}, '
            f'{old_record_info.frequency}, {old_record_info.origin_name}, '
            f'{old_record_info.unique_name}, {old_record_info.is_using} to '
            f'{new_record_info.station_id}, '
            f'{new_record_info.datetime_start_str}, '
            f'{new_record_info.datetime_stop_str}, '
            f'{new_record_info.frequency}, {new_record_info.origin_name}, '
            f'{new_record_info.unique_name}, {new_record_info.is_using}.'
        )
    returning_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returning_info


@app.get('/get-seismic-records-info/{station_id}')
def get_seismic_records_info(station_id: int) -> Response:
    """Return seismic records info from table.

    Args:
        station_id: associated with seismic record station id

    Returns: dict object with operation status, message with
    operation discription and seismic records related to station.
    """
    records_info = dbase_adapter.get_seismic_records_info(
        station_id=station_id
    )

    returning_info = Response(
        status=True,
        message=(
            f'All seismic records related to station '
            f'with id:"{station_id}" returend successfully'
        ),
        data={
            'records_info': records_info
        }
    )
    return returning_info


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host=os.getenv('APP_HOST'),
        port=int(os.getenv('APP_PORT'))
    )
