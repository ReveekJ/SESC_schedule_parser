from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Style(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Classic: _ClassVar[Style]
    Rose: _ClassVar[Style]
    PrintStream: _ClassVar[Style]
    Cyberpunk: _ClassVar[Style]
    Space: _ClassVar[Style]
    CBO: _ClassVar[Style]
    RyanGosling: _ClassVar[Style]
Classic: Style
Rose: Style
PrintStream: Style
Cyberpunk: Style
Space: Style
CBO: Style
RyanGosling: Style

class Lesson(_message.Message):
    __slots__ = ("lessonNumber", "first", "second", "third")
    LESSONNUMBER_FIELD_NUMBER: _ClassVar[int]
    FIRST_FIELD_NUMBER: _ClassVar[int]
    SECOND_FIELD_NUMBER: _ClassVar[int]
    THIRD_FIELD_NUMBER: _ClassVar[int]
    lessonNumber: int
    first: str
    second: str
    third: str
    def __init__(self, lessonNumber: _Optional[int] = ..., first: _Optional[str] = ..., second: _Optional[str] = ..., third: _Optional[str] = ...) -> None: ...

class DrawRequest(_message.Message):
    __slots__ = ("lessons", "drawStyle")
    LESSONS_FIELD_NUMBER: _ClassVar[int]
    DRAWSTYLE_FIELD_NUMBER: _ClassVar[int]
    lessons: _containers.RepeatedCompositeFieldContainer[Lesson]
    drawStyle: Style
    def __init__(self, lessons: _Optional[_Iterable[_Union[Lesson, _Mapping]]] = ..., drawStyle: _Optional[_Union[Style, str]] = ...) -> None: ...

class DrawResponse(_message.Message):
    __slots__ = ("pathToImage",)
    PATHTOIMAGE_FIELD_NUMBER: _ClassVar[int]
    pathToImage: str
    def __init__(self, pathToImage: _Optional[str] = ...) -> None: ...
