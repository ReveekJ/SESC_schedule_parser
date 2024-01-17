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
                return False, index

        return True

    def append(self, __object: ChangesType):
        if not isinstance(__object, ChangesType):
            raise TypeError('должно быть ChangesType')

        is_unique = self.__is_unique(__object)
        if is_unique:
            # если уникальное кладем в массив уже известных и возвращаемых
            super().append(__object)
            self.knowing_changes.append(__object)
        else:
            # если не уникальное - то убираем из возвращаемых, также это значит, что is_unique=False, index
            self.pop(is_unique[1])


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
