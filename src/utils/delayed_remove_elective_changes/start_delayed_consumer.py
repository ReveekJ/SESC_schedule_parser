from .consumer import DelayedCourseConsumer

from nats.aio.client import Client
from nats.js.client import JetStreamContext


async def start_delayed_consumer(
    nc: Client,
    js: JetStreamContext,
    subject: str,
    stream: str,
    durable_name: str
) -> None:
    consumer = DelayedCourseConsumer(
        nc=nc,
        js=js,
        subject=subject,
        stream=stream,
        durable_name=durable_name
    )
    await consumer.start()

