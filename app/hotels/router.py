import asyncio
from datetime import date
from typing import List
from fastapi import APIRouter

from app.exceptions import CannotBookHotelForLongPeriodException, DateFromCannotBeAfterDateToException, HotelDoesNotExistsException
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelInfo


router = APIRouter(
    prefix="/hotels",
    tags=["hotels"])


@router.get("/id/{hotel_id}")
async def get_hotel(hotel_id: int):
    hotel = await HotelDAO.find_one_or_none(id=hotel_id)
    if hotel:
        return hotel
    raise HotelDoesNotExistsException
    

@router.get("/{location}")
async def get_hotels(
    location: str, 
    date_from: date,
    date_to: date,
) -> List[SHotelInfo]:
    if date_from > date_to:
        raise DateFromCannotBeAfterDateToException
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriodException
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    return hotels