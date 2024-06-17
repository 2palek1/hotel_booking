from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ''

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="User already exists"


class IncorrectCredentialsException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Wrong email or password "


class TokenExpiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Token expired"


class TokenAbsentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Token does not exists"


class IncorrectTokenFormatException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Incorrect token format"


class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED

class RoomCannotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='No free rooms'

class HotelDoesNotExistsException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail='Hotel with this id does not exists'

class RoomsNotFoundException(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail='Rooms not found'

class DateFromCannotBeAfterDateToException(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail='date_from can not be after date_to'

class CannotBookHotelForLongPeriodException(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail='Hotel can not be booked for over a month'
    
class CannotProcessCSVException(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Can not handle CSV file"

class CannotAddDataToDatabaseException(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Can not add data to database"