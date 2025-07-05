import typing as t

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependecies import db_session
from app.services import (
    generate_csv_statistics,
    get_last_pings,
    hard_delete_address,
    insert_addresses,
    ping_all_addresses
)
from app.schemas import HostAddressInput


router = APIRouter(
    prefix="/addresses"
)


@router.post("")
async def insert_addresses_endpoint(addresses: t.List[HostAddressInput], db: AsyncSession = Depends(db_session)) -> t.Dict:
    ping_results = await insert_addresses(set([address.value for address in addresses]), db)

    return {"result": ping_results}


@router.delete("")
async def hard_delete_address_endpoint(address: str, db: AsyncSession = Depends(db_session)):
    await hard_delete_address(address, db)


@router.get("/ping_all")
async def ping_all_addresses_endpoint(db: AsyncSession = Depends(db_session)):
    await ping_all_addresses(db)


@router.get("/statistics")
async def get_csv_statisctics_endpoint(db: AsyncSession = Depends(db_session)):
    headers = {
        "Content-Disposition": "attachment; filename=statistics.csv"
    }
    return StreamingResponse(
        content=generate_csv_statistics(db),
        headers=headers,
        media_type="text/csv",
    )


@router.get("")
async def get_last_pings_endpoing(db: AsyncSession = Depends(db_session)):
    return await get_last_pings(db)


# Убрал этот роут, потому что при изменении адреса записи из истории пингов будут ссылаться на обновленный адрес, что нарушает логику
# А если не хранить в отдельной таблице хосты, то тогда тоже операция изменения смысла не имеет
# @router.patch("")
# async def alter_address_endpoint(current_address: str, new_address: str, db: AsyncSession = Depends(db_session)) -> None:
#     await alter_address(current_address, new_address, db)
