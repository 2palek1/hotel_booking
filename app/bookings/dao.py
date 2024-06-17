from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker
from app.logger import logger


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        try:
            async with async_session_maker() as session:
                """
                WITH booked_rooms AS (
                SELECT * FROM bookings
                WHERE room_id = 1 AND
                (date_from >= '2033-05-15' AND date_from <= '2033-06-20') OR
                (date_from <= '2033-05-15' AND date_to > '2033-05-15')
                )
                """
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                """
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
                LEFT JOIN booked_rooms ON booked_rooms.id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """
                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                # print(get_rooms_left.compile(engine, compile_kwargs={'literal_binds': True})

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                print(rooms_left)
                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings.__table__.columns)
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.mappings().first()
                else:
                    return None
        except(SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Canot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)


    @classmethod
    async def find_all_bookings(cls, user_id: int):
        async with async_session_maker() as session:
            get_all_bookings = (
                select(
                    Bookings.id,
                    Bookings.room_id,
                    Bookings.user_id,
                    Bookings.date_to,
                    Bookings.date_from,
                    Bookings.price,
                    Bookings.total_cost,
                    Bookings.total_days,
                    Rooms.image_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                )
                .select_from(Bookings)
                .join(Rooms, Bookings.room_id == Rooms.id)
                .where(Bookings.user_id == user_id)
            )
            user_bookings = await session.execute(get_all_bookings)
            return user_bookings.mappings().all()
