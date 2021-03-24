import sqlalchemy as sa
# функциональность ORM
import sqlalchemy.orm as orm
# объект Session, отвечающий за соединение с базой данных
from sqlalchemy.orm import Session
# модуль который поможет объявить базу данных
import sqlalchemy.ext.declarative as dec

# некоторая абстрактная декларативная база в которую позднее будем наследовать все модели
SqlAlchemyBase = dec.declarative_base()

# будем использовать для получения сессий подключения к базе данных
__factory = None


def global_init(db_file):
    """
    принимает на вход адрес базы данных, затем проверяет, не создали ли мы уже фабрику подключений
    (то есть не вызываем ли мы функцию не первый раз).
    Если уже создали, то завершаем работу, так как начальную инициализацию надо проводить только единожды.
    :param db_file:
    :return:
    """
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    # check_same_thread=False — заставляет подключение не проверять,
    # что разные объекты получаются из базы данных в разных нитях исполнения
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    # print(f"Подключение к базе данных по адресу {conn_str}")

    # Если в функцию create_engine() передать параметр echo со значением True,
    # в консоль будут выводиться все SQL-запросы, которые сделает SQLAlchemy, что очень удобно для отладки.
    engine = sa.create_engine(conn_str, echo=False)

    # создаем фабрику подключений к базе данных, которая будет работать с нужным нам движком.
    __factory = orm.sessionmaker(bind=engine)

    # Импортируем все из файла __all_models.py — именно тут SQLalchemy узнает о всех наших моделях.

    from . import __all_models
    # Наконец, заставляем нашу базу данных создать все объекты, которые она пока не создала.
    # Все таблицы, которые были уже созданы в базе данных, останутся без изменений.
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    """
    Функция create_session нужна для получения сессии подключения к нашей базе данных.
    :return:
    """
    global __factory
    return __factory()
