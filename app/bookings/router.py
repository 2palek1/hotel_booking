from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi_versioning import version
from pydantic import parse_obj_as

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SNewBooking
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users


router = APIRouter(
    prefix='/bookings',
    tags=['Bookings'],
)

@router.get("")
@version(1)
async def get_user_bookings(user: Users = Depends(get_current_user)):
    return await BookingDAO.find_all_bookings(user.id)


@router.post("")
@version(2)
async def add_booking(
        # background_tasks: BackgroundTasks,
    data: SNewBooking,
    user: Users = Depends(get_current_user)
):
    booking = await BookingDAO.add(
        user.id,
        data.room_id,
        data.date_from,
        data.date_to
    )
    if not booking:
        raise RoomCannotBeBooked
    # print(booking)
    # booking = parse_obj_as(SBooking, booking).dict()
    # celery
    #send_booking_confirmation_email.delay(booking, 'ashimov.ashat05@gmail.com')
    # background tasks
    # background_tasks.add_task(send_booking_confirmation_email, booking, "ashimov.ashat05@gmail.com")
    return booking


@router.delete("/{booking_id}")
@version(1)
async def delete_booking(
    booking_id: int,
    current_user: Users = Depends(get_current_user)
):
    return await BookingDAO.delete(id=booking_id, user_id=current_user.id)

