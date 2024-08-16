from nats.js.api import StreamConfig, RetentionPolicy, StorageType
from nats.js.client import JetStreamContext


async def create_delayed_elective_changes_stream(js: JetStreamContext):
    # Настройка стрима с заданными параметрами
    stream_config = StreamConfig(
        name="delayed_elective_changes",  # Название стрима
        subjects=[
            'elective.delayed.changes'
        ],
        retention=RetentionPolicy.LIMITS,  # Политика удержания
        max_bytes=300 * 1024 * 1024,  # 300 MiB
        max_msg_size=10 * 1024 * 1024,  # 10 MiB
        storage=StorageType.FILE,  # Хранение сообщений на диске
        allow_direct=True,  # Разрешение получать сообщения без создания консьюмера
    )

    await js.add_stream(stream_config)
