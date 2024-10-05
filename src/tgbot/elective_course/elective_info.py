import datetime
from enum import Enum


class ElectiveInfo(Enum):
    elective_times = sorted([datetime.time(8, 10), datetime.time(11, 40), datetime.time(15, 30),
                             datetime.time(19, 0), datetime.time(19, 40), datetime.time(17, 0),
                             datetime.time(18, 15), datetime.time(14, 15), datetime.time(13, 15),
                             datetime.time(18, 30), datetime.time(20, 0), datetime.time(21, 0),
                             datetime.time(9, 0), datetime.time(17, 30)])
    date_format: str = '%H:%M'