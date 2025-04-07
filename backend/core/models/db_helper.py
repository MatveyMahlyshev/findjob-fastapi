from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)
from asyncio import current_task

from core.config import settings

class DataBaseHelper:
    def __init__(self, url: str, echo: bool = False):

        # создание асинхронного движка
        self.engine = create_async_engine(
            url=settings.db.url,  # добавление адреса бд
            echo=settings.db.echo,  # логи запросов
        )

        # создание сессии
        self.session_factory = async_sessionmaker(
            bind=self.engine,  # привязка сессии к раннее созданному движку
            autoflush=False,  # автоматическая синхронизация изменения объектов перед запросом в бд
            autocommit=False,  # автоматическая фиксация изменений в бд
            expire_on_commit=False,  # удаление объекта после завершения сесии
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def scoped_session_dependency(self):
        session = self.get_scoped_session()
        yield session
        await session.close()


# создание экземпляра класса дбх
db_helper = DataBaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)
