"""Microservice main module."""

import os

import dotenv
import uvicorn
from fastapi import FastAPI

from dbase_api_server.containers import PostgresConnectionParams
from dbase_api_server.dbase import StorageDBase
from dbase_api_server.models import Deposit, Response

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
    returned_info = Response(
        status=True,
        message='Service is alive',
        data={}
    )
    return returned_info.dict()


@app.get('/get-all-deposits')
def get_all_deposits() -> dict:
    """Return all deposits name from deposit table.

    Returns: dict object with operation status, message with
    operation discription and all deposit area names.
    """
    area_names = dbase_adapter.get_all_deposit_names()
    if area_names is None:
        area_names = []

    returned_info = Response(
        status=True,
        message='All deposits name returns successfully',
        data={
            'area_names': area_names
        }
    )
    return returned_info.dict()


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

    returned_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returned_info.dict()


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

    returned_info = Response(
        status=is_added,
        message=message,
        data={}
    )
    return returned_info.dict()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host=os.getenv('APP_HOST'),
        port=int(os.getenv('APP_PORT'))
    )
