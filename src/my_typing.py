import asyncio
import sys

from src.database import get_async_session
from src.tgbot.changes.changes_db import ChangesDB
from src.tgbot.changes.schemas import ChangesType


class UnchangeableType:
    def __init__(self):
        self.count_of_change = 0

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __set__(self, instance, value):
        if self.count_of_change < 3:
            self.count_of_change += 1
            return setattr(instance, self.name, value)
        else:
            raise ValueError('You can not change this attribute')

    def __get__(self, instance, owner):
        return getattr(instance, self.name)


# при попытке например пройтись по этому типу данных будет выполнен проход по self как в массиве
class ChangesList(list):
    def __init__(self):
        # список уже известных изменений
        self.knowing_changes = asyncio.get_event_loop().run_until_complete(self.__get_knowing_changes_from_db())
        super().__init__([])  # список с теми изменениями, которые мы будем возвращать

    @staticmethod
    async def __get_knowing_changes_from_db() -> list[ChangesType]:
        session = await get_async_session()
        res = await ChangesDB.get_all_changes(session)
        await session.close()

        return res

    # проверка на уникальность
    def __is_unique(self, __object: ChangesType) -> bool | tuple[bool, int] | None:
        # проверка на присутствие такого же расписания
        for index, elem in enumerate(self.knowing_changes):
            # проверка по diffs во избежание ошибок (почему-то бывают ошибки в lessons)
            if elem.schedule.get('diffs') == __object.schedule.get('diffs'):
                try:
                    return False, self.index(__object)  # Работа метода index в этом случае изменена, см. метод
                # Если возникает эта ошибка, то мы просто игнорим. Я так и не разобрался почему она возникает
                except ValueError:
                    return None
                except Exception as e:
                    print(e)
        return True

    async def append(self, __object: ChangesType):
        if not isinstance(__object, ChangesType):
            raise TypeError('должно быть ChangesType')
        # если __object.schedule.get('diffs') is None, то дальнейшие действия бесполезны
        if __object.schedule.get('diffs') is None:
            return None

        is_unique = self.__is_unique(__object)
        if isinstance(is_unique, bool):
            # если уникальное кладем в массив уже известных и возвращаемых
            session = await get_async_session()

            super().append(__object)
            self.knowing_changes.append(__object)

            await ChangesDB.add_changes(session, __object)
            await session.close()
        elif is_unique is None:
            return None
        else:
            # если не уникальное - то убираем из возвращаемых, также это значит, что is_unique = False, index
            self.pop(is_unique[1])

    # внимание измененное поведения для index при поиске ChangesType
    def index(self, __value, __start=0, __stop=sys.maxsize):
        if isinstance(__value, ChangesType):
            elem: ChangesType
            for index, elem in enumerate(self):
                # этих 3 параметров будет достаточно, тк использовать будет только в контексте метода __is_unique
                if elem.type == __value.type and elem.second == __value.second and elem.weekday == __value.weekday:
                    return index
        super().index(__value, __start, __stop)


# Порядок ввода: tuple(краткое имя, русское вариант) ......
class TextMessage:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self, *args):
        self.__text = self.__args_to_dict(args)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        raise ValueError('You can not change this attribute')

    @classmethod
    def __args_to_dict(cls, arguments: tuple):
        res = {'ru': {},
               'en': {}}

        for i in arguments:
            for index, value in enumerate(i):
                if index % 3 == 1:
                    res['ru'][i[0]] = value
                elif index % 3 == 2:
                    res['en'][i[0]] = value
                else:
                    continue
        return res

    def __call__(self, short_name_text_mes: str, lang: str):
        return self.__text[lang][short_name_text_mes]
