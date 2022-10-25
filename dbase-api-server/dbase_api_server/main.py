"""Microservice main module."""

import os

import dotenv
from fastapi import FastAPI

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
        dbname=os.getenv('POSTGRES_DBASE')
    )
)


@app.get('/get-all-deposits')
def get_all_deposits() -> dict:
    """Return all deposits name from deposit table.

    Returns: dict object with operation status, message with
    operation discription and all deposit area names.
    """
    area_names = dbase_adapter.get_all_deposit_names()
    container = ResponseContainer(
        status=True,
        message='All deposits name returns successfully',
        data={
            'area_names': area_names
        }
    )
    return container.convert_to_dict()


@app.post('/add-deposit')
def add_new_deposit_name(area_name: str) -> bool:
    """Add deposit info to database.

    Args:
        area_name: deposit area name

    Returns: dict object with request status, message with
    action discription and added deposit area name.
    """
    add_new_area_name = dbase_adapter.add_deposit_info(area_name)
    container = ResponseContainer(
        status=add_new_area_name,
        message=f'Deposit name \"{area_name}\" added successfully',
        data={
            'area_name': area_name
        }
    )
    return container.convert_to_dict()


@app.post('/update-deposit')
def update_deposit_name(old_area_name: str, new_area_name: str) -> bool:
    """Update deposit name.

    Args:
        old_area_name: deposit area name
        new_area_name: updated deposit area name

    Returns: dict object with request status, message with
    action discription and updated deposit area name.
    """
    update_area_name = dbase_adapter.update_deposit_name(old_area_name,
                                                         new_area_name)
    container = ResponseContainer(
        status=update_area_name,
        message=f'Deposit \"{old_area_name}\" successfully '
                'renamed to \"{new_area_name}\"',
        data={
            'old_area_name': old_area_name,
            'new_area_name': new_area_name
        }
    )
    return container.convert_to_dict()
