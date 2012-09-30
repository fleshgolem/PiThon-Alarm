from sqlalchemy import create_engine, Table, Column, Integer, MetaData, DateTime

engine = create_engine('sqlite:///alarm.db', echo=True)
metadata = MetaData()
alarms = Table('alarms', metadata, Column('id', Integer, primary_key=True), Column('date', DateTime))
metadata.create_all(engine) 