from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.database.models import CarModel

class CarRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_cars_bulk(self, cars_data: list[dict]):
        """
        Массовое сохранение автомобилей с логикой ON CONFLICT DO NOTHING
        (Аналог INSERT OR IGNORE в SQLite)
        """
        if not cars_data:
            return

        # Используем специальный insert из диалекта PostgreSQL
        stmt = insert(CarModel).values(cars_data)
        
        # Если ID уже существует, мы просто ничего не делаем (DO NOTHING)
        stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
        
        try:
            self.session.execute(stmt)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e