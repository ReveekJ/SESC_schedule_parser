import grpc

from proto import drawing_pb2_grpc, drawing_pb2


def render_example_image(style: int) -> str:
    with grpc.insecure_channel('drawing:8080') as channel:
        stub = drawing_pb2_grpc.DrawerStub(channel)
        dct: dict[str, str] = {str(value): key for key, value in drawing_pb2.Style.items()}

        class_lessons = [
            drawing_pb2.Lesson(lessonNumber=1, first='Math', second='101', third='Mr. Smith'),
            drawing_pb2.Lesson(lessonNumber=2, first='Science', second='102', third='Mrs. Johnson')
        ]

        request = drawing_pb2.DrawRequest(
            lessons=class_lessons,
            drawStyle=dct[str(style)]
        )

        response: drawing_pb2.DrawResponse = stub.Draw(request)
        return response.pathToImage
