from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Rooms(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    hotel_id = Column(ForeignKey("hotels.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(JSON)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer, nullable=False)

    hotel = relationship("Hotels", back_populates="rooms")
    booking = relationship("Bookings", back_populates="room")

    def __str__(self) -> str:
        return f"Room {self.id} {self.name}"