# %%
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.base import Base
from app.data.connection import TeamPlayerSalary, get_session
from app.data.league import PlayerSeason

DATABASE_URL = (
    "postgresql+psycopg://athlete_user:athlete_password@localhost:6543/athlete_market"
)

engine = create_engine(
    DATABASE_URL, echo=True
)  # echo=True prints SQL queries for debugging

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
session = Session(engine)

ps = session.execute(select(PlayerSeason).join(TeamPlayerSalary)).scalars().all()

# %%
from matplotlib import pyplot as plt

plt.boxplot(x=[s.age for s in ps], vert=[s.relative_dollars for s in ps])

# %%
