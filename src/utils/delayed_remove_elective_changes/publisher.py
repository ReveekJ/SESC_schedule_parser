from nats.js.client import JetStreamContext
from datetime import datetime


async def delay_changes_removing(
    js: JetStreamContext,
    course_id: int,
    subject: str,
    removing_time: datetime
) -> None:
    now = datetime.now()
    delay = (removing_time - now).seconds
    headers = {
        'Elective-Delayed-Course-ID': str(course_id),
        'Elective-Delayed-Course-Timestamp': str(now.timestamp()),
        'Elective-Delayed-Course-Delay': str(delay),
    }
    await js.publish(subject=subject, headers=headers)
