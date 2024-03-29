from sqlalchemy import MetaData, Table, Column, Text

metadata = MetaData()
columns_json = {0: 'id',
                1: 'role',
                2: 'sub_info',
                3: 'lang'}

users = Table('users',
              metadata,
              Column(columns_json[0], Text, primary_key=True),
              Column(columns_json[1], Text),
              Column(columns_json[2], Text),
              Column(columns_json[3], Text)
              )

changes = Table('changes',
                metadata,
                Column('type', Text, nullable=False),
                Column('second', Text, nullable=False),
                Column('weekday', Text, nullable=False),
                Column('schedule', Text, nullable=False))
