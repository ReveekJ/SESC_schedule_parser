import sys


class ChangesType:
    def __init__(self, _type, _second, _weekday, _schedule):
        self.type = _type
        self.second = _second
        self.weekday = _weekday
        self.schedule = _schedule


# при попытке например пройтись по этому типу данных будет выполнен проход по self как в массиве
class ChangesList(list):
    def __init__(self):
        self.knowing_changes = []  # список уже известных изменений
        super().__init__([])  # список с теми изменениями, которые мы будем возвращать

    # проверка на уникальность
    def __is_unique(self, __object: ChangesType) -> bool | tuple[bool, int]:
        # проверка на присутствие такого же расписания
        for index, elem in enumerate(self.knowing_changes):
            # проверка по diffs во избежание ошибок (почему-то бывают ошибки в lessons)
            if elem.schedule.get('diffs') == __object.schedule.get('diffs'):
                return False, self.index(__object)  # Работа метода index в этом случае изменена, см. метод

        return True

    def append(self, __object: ChangesType):
        if not isinstance(__object, ChangesType):
            raise TypeError('должно быть ChangesType')

        is_unique = self.__is_unique(__object)
        if isinstance(is_unique, bool):
            # если уникальное кладем в массив уже известных и возвращаемых
            super().append(__object)
            self.knowing_changes.append(__object)
        else:
            # если не уникальное - то убираем из возвращаемых, также это значит, что is_unique=False, index
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
