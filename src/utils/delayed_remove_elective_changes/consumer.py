from datetime import datetime, timedelta, timezone

from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

from src.tgbot.elective_course.elective_course import ElectiveCourseDB


class DelayedCourseConsumer:
    def __init__(
            self,
            nc: Client,
            js: JetStreamContext,
            subject: str,
            stream: str,
            durable_name: str
    ) -> None:
        self.nc = nc
        self.js = js
        self.subject = subject
        self.stream = stream
        self.durable_name = durable_name

    async def start(self) -> None:
        self.stream_sub = await self.js.subscribe(
            subject=self.subject,
            stream=self.stream,
            cb=self.on_message,
            durable=self.durable_name,
            manual_ack=True
        )

    async def on_message(self, msg: Msg):
        # Получаем из заголовков сообщения время отправки и время задержки
        sent_time = datetime.fromtimestamp(float(msg.headers.get('Elective-Delayed-Course-Timestamp')), tz=timezone.utc)
        delay = int(msg.headers.get('Elective-Delayed-Course-Delay'))

        # Проверяем наступило ли время обработки сообщения
        if sent_time + timedelta(seconds=delay) > datetime.now().astimezone():
            # Если время обработки не наступило - вычисляем сколько секунд осталось до обработки
            new_delay = (sent_time + timedelta(seconds=delay) - datetime.now().astimezone()).total_seconds()
            # Отправляем nak с временем задержки
            await msg.nak(delay=new_delay)
        else:
            course_id = int(msg.headers.get('Elective-Delayed-Course-ID'))
            # Если время обработки наступило - пытаемся удалить сообщение в чате
            course = await ElectiveCourseDB.get_course_by_id(course_id)
            await ElectiveCourseDB.remove_changes(course)

            await msg.ack()

    async def unsubscribe(self) -> None:
        if self.stream_sub:
            await self.stream_sub.unsubscribe()
