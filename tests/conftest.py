from dotenv import load_dotenv  # noqa: E402

load_dotenv(".env.test", override=True)# noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from testcontainers.community.postgres import PostgresContainer  # noqa: E402

from saga_plus_simulator import models  # noqa: E402
from saga_plus_simulator.database import Base, get_db  # noqa: E402
from saga_plus_simulator.main import app  # noqa: E402


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container





@pytest.fixture(scope="session")
def engine(postgres_container):
    url = postgres_container.get_connection_url().replace("psycopg2", "psycopg")
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    yield engine



@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()


    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_product(db_session):
    product = models.Product(name="Sample Product", price=1000)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product
@pytest.fixture
def sample_order(db_session, sample_product):
    order = models.Order(product_id=sample_product.id, quantity=2)
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order
