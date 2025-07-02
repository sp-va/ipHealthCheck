import typing as t
import io
import csv

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, update, select, desc
from fastapi import status
from fastapi.responses import JSONResponse, Response

from app.db.models import HealthCheckHistory, HostAddresses
from app.ping import run_multithread_pings
from app.schemas import HostAddressInput, PingOutput


async def insert_addresses(
        addresses: t.Set[str],
        db: AsyncSession
) -> t.List:
    raised_exceptions = set()

    for address in addresses:
        try:
            savepoint = await db.begin_nested()
            db.add(HostAddresses(ip_address=address))
            await db.flush()
        except:
            raised_exceptions.add(address)
            await savepoint.rollback()
    await db.commit()

    remaining_addresses = addresses - raised_exceptions

    ping_outputs = await run_multithread_pings(remaining_addresses)
    for ping in ping_outputs:
        await insert_ping_output(ping, db)

    return ping_outputs

async def hard_delete_address(
        address: str,
        db: AsyncSession
):
    try:
        stmt = delete(HostAddresses).where(HostAddresses.ip_address == address)
        await db.execute(stmt)
    except Exception as ex:
        await db.rollback()
        return JSONResponse(content=str(ex), status_code=status.HTTP_400_BAD_REQUEST)
    await db.commit()
    return Response(content="Адрес удален", status_code=status.HTTP_204_NO_CONTENT)


async def alter_address(
        current_address: str,
        new_address: str,
        db: AsyncSession
):
    try:
        stmt = update(HostAddresses).where(HostAddresses.ip_address == current_address).values(ip_address=new_address)
        await db.execute(stmt)
    except:
        await db.rollback()
        return
    await db.commit()


async def insert_ping_output(
        ping_output: PingOutput,
        db: AsyncSession
):
    try:
        db.add(
            HealthCheckHistory(
                ping_time=ping_output.avg_ping_ms,
                delivered_packages_percentage=100-ping_output.packet_loss if ping_output.packet_loss is not None else None,
                related_address=ping_output.address
            )
        )
    except:
        await db.rollback()
        return
    await db.commit()

async def ping_all_addresses(
        db: AsyncSession
):
    stmt = select(HostAddresses)
    addresses = await db.execute(stmt)  # при большом кол-ве записей такой вариант плохо работает, так как сразу все в память грузится
    addresses = addresses.scalars().all()

    ping_outputs = await run_multithread_pings(set([address.ip_address for address in addresses]))
    for ping in ping_outputs:
        await insert_ping_output(ping, db)


async def generate_csv_statistics(db: AsyncSession):
    stmt = select(HealthCheckHistory)
    history = (await db.execute(stmt)).scalars().all()

    with io.StringIO() as buffer:
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["id", "ping_time", "delivered_pakages_percentage", "last_ping", "address"])

        for p in history:
            writer.writerow([
                p.id,
                p.ping_time,
                p.delivered_packages_percentage,
                p.last_successful_ping_timestamp,
                p.related_address
            ])
        buffer.seek(0)
        yield buffer.read()



async def get_last_pings(db: AsyncSession):
    stmt = select(HealthCheckHistory).distinct(HealthCheckHistory.related_address).order_by(
        HealthCheckHistory.related_address,
        desc(HealthCheckHistory.last_successful_ping_timestamp)
    )
    pings = (await db.execute(stmt)).scalars().all()
    return pings