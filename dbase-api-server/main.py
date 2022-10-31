"""Microservice main module."""

import os

import dotenv
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from dbase_api_server.containers import (PostgresConnectionParams,
                                         ResponseContainer)
from dbase_api_server.dbase import StorageDBase

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


class Deposits(BaseModel):
    """Model with field for adding new deposit.

    Args:
        area_name: deposit name for adding

    """
    area_name: str


class UpdateDeposits(BaseModel):
    """Model with fields for renaming deposit area name.

    Args:
        old_area_name: initial area name
        new_area_name: area name for renaming

    """
    old_area_name: str
    new_area_name: str


@app.get('/ping')
def check_service_alive() -> dict:
    """Return ping-pong response.

    Returns: dict object with status and message

    """
    container = ResponseContainer(
        status=True,
        message='Service is alive',
        data={}
    )
    return container.convert_to_dict()


@app.get('/get-all-deposits')
def get_all_deposits() -> dict:
    """Return all deposits name from deposit table.

    Returns: dict object with operation status, message with
    operation discription and all deposit area names.
    """
    area_names = dbase_adapter.get_all_deposit_names()
    if area_names is None:
        area_names = []

    container = ResponseContainer(
        status=True,
        message='All deposits name returns successfully',
        data={
            'area_names': area_names
        }
    )
    return container.convert_to_dict()


@app.post('/add-deposit')
def add_new_deposit_name(deposits: Deposits) -> dict:
    """Add deposit info to database.

    Args:
        deposits: Deposits model with area_name field

    Returns: dict object with request status, message with
    action discription and added deposit area name.
    """
    is_added = dbase_adapter.add_deposit_info(deposits.area_name)
    if is_added:
        message = f'Deposit name "{deposits.area_name}" added successfully'
    else:
        message = f'Cant add deposit name "{deposits.area_name}"'

    container = ResponseContainer(
        status=is_added,
        message=message,
        data={}
    )
    return container.convert_to_dict()


@app.post('/update-deposit')
def update_deposit_name(update_deposits: UpdateDeposits) -> dict:
    """Update deposit name.

    Args:
        update_deposits: UpdateDeposits model with old_area_name and
        new area_name fields

    Returns: dict object with request status, message with
    action discription and updated deposit area name.
    """
    is_added = dbase_adapter.update_deposit_name(update_deposits.old_area_name,
                                                 update_deposits.new_area_name)
    if is_added:
        message = (f'Deposit "{update_deposits.old_area_name}" successfully '
                   f'renamed to "{update_deposits.new_area_name}"')
    else:
        message = (f'Cant rename "{update_deposits.old_area_name} to '
                   f'"{update_deposits.new_area_name}"')

    container = ResponseContainer(
        status=is_added,
        message=message,
        data={}
    )
    return container.convert_to_dict()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host=os.getenv('APP_HOST'),
        port=int(os.getenv('APP_PORT'))
    )
