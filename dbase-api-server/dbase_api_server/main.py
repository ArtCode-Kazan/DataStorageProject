"""Microservice main module."""

import os

import dotenv
from fastapi import FastAPI

from dbase_api_server.containers import PostgresConnectionParams
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
def get_all_deposits() -> bool:
    """Return all deposits name from deposit table.

    Returns: True if query completed success, False - if not.
    """
    return dbase_adapter.get_all_deposit_names()


@app.post('/add-deposit')
def add_new_deposit_name(area_name: str) -> bool:
    """Add deposit info to database.

    Args:
        area_name: deposit area name

    Returns: True if name added success, False - if not.
    """
    return dbase_adapter.add_deposit_info(area_name)


@app.post('/update-deposit')
def update_deposit_name(old_area_name: str, new_area_name: str) -> bool:
    """Update deposit name.

    Args:
        old_area_name: deposit area name
        new_area_name: updated deposit area name

    Returns: True if name updated success, False - if not.
    """
    return dbase_adapter.update_deposit_name(old_area_name, new_area_name)
