from sqlalchemy import MetaData, Table, Column, Integer, Text

metadata = MetaData()
users = Table('users',
              metadata,
              Column('id', Integer, primary_key=True),
              Column('role', Text),
              Column('sub_info', Text))
