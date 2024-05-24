import datetime
import time
from typing import Any

import aiohttp
import simplejson as json

from fastapi import APIRouter


class LycregAPI:
    SESC_JSON = {
        "subject_list": {},
        "teach_list": {},
        "current_week_days": {},
        "cache_subj_list": 0,
        "cache_teach_list": 0,
        "cache_week_days": {},
        "default_subjects": {
            "s110": "Русский язык",
            "s120": "Литература",
            "s210": "Английский язык",
            "s220": "Немецкий язык",
            "s230": "Французский язык",
            "s310": "Искусство",
            "s320": "МХК",
            "s330": "Музыка",
            "s410": "Математика",
            "s420": "Алгебра",
            "s430": "Алгебра и начала анализа",
            "s440": "Геометрия",
            "s450": "Информатика",
            "s510": "История",
            "s520": "История России",
            "s530": "Всеобщая история",
            "s540": "Обществознание",
            "s550": "Экономика",
            "s560": "Право",
            "s570": "География",
            "s610": "Физика",
            "s620": "Астрономия",
            "s630": "Химия",
            "s640": "Биология",
            "s710": "Технология",
            "s810": "Физическая культура",
            "s820": "ОБЖ",
        },
        "full_marks": {
            "0": "н/а",
            "2": "2 (неуд.)",
            "3": "3 (удовл.)",
            "4": "4 (хор.)",
            "5": "5 (отл.)",
            "999": "зач.",
        },
        "all_dtsit": {
            'd205a': ['1ч', 'Первая четверть', 'd001', 'd205'], 'd331b': ['2ч', 'Вторая четверть', 'd206', 'd331'],
            'd628d': ['3ч', 'Третья четверть', 'd401', 'd628'], 'd915e': ['4ч', 'Четвертая четверть', 'd629', 'd915'],
            'd331c': ['1п', 'Первое полугодие', 'd001', 'd331'], 'd915f': ['2п', 'Второе полугодие', 'd401', 'd915'],
            'd925g': ['Год', 'Учебный год', 'd001', 'd925']
        },
        "dtsit": {
            "d205a": ["1ч", "Первая четверть", "d001", "d205"],
            "d331b": ["2ч", "Вторая четверть", "d206", "d331"],
            "d628d": ["3ч", "Третья четверть", "d401", "d628"],
            "d915e": ["4ч", "Четвертая четверть", "d629", "d915"],
        },
        "weights": ['0', '0.5', '', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0'],
        "scole_domain": "https://lycreg.urfu.ru/"
    }

    def __init__(self, client: aiohttp.ClientSession):
        self.client = client

    async def __authorise_raw_request(self, captcha: str, captcha_id: str, user_login: str, user_password: str) -> str:
        async with self.client.post(
                'https://lycreg.urfu.ru/',
                data=f'{{"t":"pupil", "l":"{user_login}", "p":"{user_password}", "f":"login", '
                     f'"ci":{captcha_id}, "c":{captcha} }}',
        ) as response:
            assert response.status == 200, 'Login-function response is not 200'
            return await response.text()

    async def __tabel_get_raw_request(self, user_login: str, user_token: str) -> str:
        async with self.client.post(
                'https://lycreg.urfu.ru/',
                data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"tabelGet","z":["{user_login}"]}}',
        ) as response:
            assert response.status == 200, 'tabelGet-function response is not 200'
            return await response.text()

    async def __subj_list_raw_request(self, user_login: str, user_token: str) -> str:
        async with self.client.post(
                'https://lycreg.urfu.ru/',
                data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"subjList"}}',
        ) as response:
            assert response.status == 200, 'subjList-function response is not 200'
            return await response.text()

    async def __teach_list_raw_request(self, user_login: str, user_token: str) -> str:
        async with self.client.post(
                'https://lycreg.urfu.ru/',
                data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"teachList"}}',
        ) as response:
            assert response.status == 200, 'teachList-function response is not 200'
            return await response.text()

    async def __journal_get_raw_request(self, user_login: str, user_token: str) -> str:
        async with self.client.post(
                'https://lycreg.urfu.ru/',
                data=f'{{"t":"pupil","l":"{user_login}","p":"{user_token}","f":"jrnGet","z":[]}}',
        ) as response:
            assert response.status == 200, 'jrnGet-function response is not 200'
            return await response.text()

    async def lycreg_authorise(self, user_login: str, user_password: str) -> dict:
        captcha_bytes, captcha_id = await self.__fetch_captcha()
        assert captcha_id is not None, 'X-Cpt header doesn\'t exists'
        solved_captcha = await self.__solve_captcha(captcha_bytes)
        authorise = await self.__authorise_raw_request(captcha=solved_captcha, captcha_id=captcha_id,
                                                       user_login=user_login, user_password=user_password)
        if 'token' not in authorise:
            return {'error': 'auth error'}
        if '["pupil"]' not in authorise:
            return {'error': 'role error'}
        return json.loads(authorise)

    async def __fetch_captcha(self) -> tuple[bytes, str | None]:
        async with self.client.get(f'{self.SESC_JSON["scole_domain"]}cpt.a') as response:
            assert response.status == 200, '/cpt.a response status is not 200'
            return await response.read(), response.headers.get('X-Cpt')

    @staticmethod
    async def __solve_captcha(captcha_bytes: bytes) -> str:
        # idk how but it works
        columns_pairs = {(524287, 458759): 0, (24579, 49155): 0, (7, 131071): 1, (415, 111): 1, (126983, 258079): 2,
                         (24591, 57371): 2, (519935, 462343): 3, (115459, 99075): 3, (63503, 524287): 4, (227, 451): 4,
                         (261951, 523903): 5, (24831, 6159): 5, (465927, 516095): 6, (15111, 29443): 6,
                         (460799, 524287): 7, (24591, 12303): 7, (524287, 462343): 8, (27, 15): 8,
                         (459207, 459143): 9, (57731, 49347): 9}
        num2i = {0: 0, 1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6, 128: 7, 256: 8, 512: 9, 1024: 10, 2048: 11,
                 4096: 12,
                 8192: 13, 16384: 14, 32768: 15, 65536: 16, 131072: 17, 262144: 18, 524288: 19, 1048576: 20,
                 2097152: 21,
                 4194304: 22, 8388608: 23, 16777216: 24, 33554432: 25, 67108864: 26, 134217728: 27, 268435456: 28,
                 536870912: 29, 1073741824: 30, 2147483648: 31}
        _data = captcha_bytes[104:-20]
        _numbers = (int(_data[i: 3630: 121].replace(b'\x00', b'0').replace(b'\x01', b'1'), 2) for i in range(121))
        _columns = [n >> num2i[n & -n] for n in _numbers]
        _solution, _wait_for_0 = '', False
        for i in range(120):
            _pair = _columns[i], _columns[i + 1]
            if _wait_for_0 and _pair[1] == 0:
                _wait_for_0 = False
            elif _pair in columns_pairs:
                _solution += str(columns_pairs[_pair])
                _wait_for_0 = True
        return _solution

    async def __get_subj_list(self, user_login: str, user_token: str, no_cache=False) -> dict:
        """
        Returns a dictionary where the key is the subject code, and the value is the full name.
        Cached: 3 days
        """
        _x = self.SESC_JSON.get('subject_list')
        if _x is not None and not no_cache and time.time() - self.SESC_JSON.get('^cache_subj_list', 0) < 259200:
            return self.SESC_JSON['default_subjects'] | _x
        # update cache
        self.SESC_JSON['^cache_subj_list'] = time.time()
        self.SESC_JSON['subject_list'] = json.loads(
            await self.__subj_list_raw_request(user_login=user_login, user_token=user_token)
        )
        return self.SESC_JSON['default_subjects'] | self.SESC_JSON['subject_list']

    async def __get_teach_list(self, user_login: str, user_token: str, no_cache=False) -> dict:
        """
        Returns a dictionary where the key is the login, and the value is the teacher's full name.
        Cached: 3 days
        """
        _x = self.SESC_JSON.get('teach_list')
        if _x is not None and not no_cache and time.time() - self.SESC_JSON.get('^cache_teach_list', 0) < 259200:
            return _x
        # update cache
        self.SESC_JSON['^cache_teach_list'] = time.time()
        self.SESC_JSON['teach_list'] = {
            i['login']: i['fio'] for i in json.loads(
                await self.__teach_list_raw_request(user_login=user_login, user_token=user_token)
            )
        }
        return self.SESC_JSON['teach_list']

    async def __get_week_days(self, week_shift=0, no_cache=False) -> dict[Any, Any] | int | Any:
        assert week_shift <= 0, 'week_shift must be <= 0'
        week_shift = -week_shift

        # return cache (by days)
        _x = self.SESC_JSON.get(f'current_week_days_{week_shift}')
        _now = datetime.datetime.now()
        _cache_time = self.SESC_JSON.get(f'^cache_week_days_{week_shift}', _now - datetime.timedelta(days=7))
        if _x is not None and _cache_time.strftime('%Y-%m-%d') == _now.strftime('%Y-%m-%d') and not no_cache:
            return _x

        # update cache
        self.SESC_JSON[f'^cache_week_days_{week_shift}'] = _now
        _now -= datetime.timedelta(days=week_shift * 7)
        self.SESC_JSON[f'current_week_days_{week_shift}'] = (
            [
                await self.__date_convert((_now - datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
                for i in range(1, _now.weekday() + 1)
            ] + [
                await self.__date_convert((_now + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
                for i in range(7 - _now.weekday())
            ],
            (_now - datetime.timedelta(days=_now.weekday())).strftime('%d.%m.%Y'),
            (_now + datetime.timedelta(days=6 - _now.weekday())).strftime('%d.%m.%Y'),
        )
        return self.SESC_JSON[f'current_week_days_{week_shift}']

    async def __get_day(self, day_shift=0) -> tuple[str, str]:
        _now = datetime.datetime.now()
        return (
            await self.__date_convert((_now - datetime.timedelta(days=-day_shift - 1)).strftime('%Y-%m-%d')),
            (_now - datetime.timedelta(day_shift)).strftime('%d.%m.%Y'),
        )

    @staticmethod
    async def __date_convert(data_inp: str, full=0) -> str:
        # translated to python from ini.js (scole)
        if '-' in data_inp:
            y, m, d, *_ = data_inp.split('-')
            m_num = int(m)
            m = m_num + (-9 if m_num > 8 else 3)
            return f'd{m}{d}'
        elif '.' in data_inp:
            d, m, *_ = data_inp.split('.')
            m_num = int(m)
            m = m_num + (-9 if m_num > 8 else 3)
            return f'd{m}{d}'
        else:
            m_num = int(data_inp[1])
            d = data_inp[2:4]
            m = f'{m_num + (9 if m_num < 4 else -3):0>2}'
            if full:
                date_obj = datetime.datetime.now()
                y = date_obj.year
                curr_m = date_obj.month
                if m_num < 4 and curr_m < 8:
                    y -= 1
                return f'{y}-{m}-{d}'
            else:
                return f'{d}.{m}'

    async def get_grades(self,
                         user_login: str,
                         user_password: str,
                         week_shift=0,
                         ) -> tuple[int, str]:
        _auth = await self.lycreg_authorise(
            user_login=user_login,
            user_password=user_password,
        )
        if _auth.get('error') is not None:
            return 1, _auth['error']
        _user_token = _auth['token']

        _journal = await self.__journal_get_raw_request(
            user_login=user_login,
            user_token=_user_token,
        )
        if _journal == 'none':
            return 1, 'no jornal'
        _journal = json.loads(_journal)

        _teachers = await self.__get_teach_list(
            user_login=user_login,
            user_token=_user_token,
        )
        _subjects = await self.__get_subj_list(
            user_login=user_login,
            user_token=_user_token,
        )
        _current_weekday_code, _week_start, _week_end = await self.__get_week_days(week_shift if week_shift <= 0 else 0)

        _render = ''
        for _subject_teacher, _lessons in _journal.items():
            _, _subject, _teacher_login, _marks = *_subject_teacher.split('_'), ''
            for _date_code, _lesson in _lessons.items():
                if _date_code not in _current_weekday_code:
                    continue
                _, _, _weight, *_mark = _lesson
                if not _mark or not _mark[-1]:
                    continue
                for _mark in _mark[-1].split(' '):
                    _marks += f'{_mark}{(" (Вес: " + j + ")") if (j := self.SESC_JSON["weights"][_weight]) else ""}, '
            if _marks:
                _render += f'\n\n<i>{_subjects.get(_subject)} - {_teachers.get(_teacher_login)}</i>\n<b>{_marks[:-2]}</b>'

        return 0, (
            f'<b>Оценки за неделю</b> <i>({_week_start} - {_week_end})</i>{_render}'
            if _render else f'{"<b>За неделю оценки не получены</b>"} <i>({_week_start} - {_week_end})</i>'
        )

    async def get_homework(self,
                           user_login: str,
                           user_password: str,
                           day_shift=0,
                           ) -> tuple[int, str]:
        _auth = await self.lycreg_authorise(
            user_login=user_login,
            user_password=user_password,
        )
        if _auth.get('error') is not None:
            return 1, _auth['error']
        _user_token = _auth['token']

        _journal = await self.__journal_get_raw_request(
            user_login=user_login,
            user_token=_user_token,
        )
        if _journal == 'none':
            return 1, 'no jornal'
        _journal = json.loads(_journal)

        teachers = await self.__get_teach_list(
            user_login=user_login,
            user_token=_user_token,
        )
        subjects = await self.__get_subj_list(
            user_login=user_login,
            user_token=_user_token,
        )
        _day_code, _day = await self.__get_day(day_shift)
        _render = ''
        for _subject_teacher, _lessons in _journal.items():
            _class, _subject, _teacher_login = _subject_teacher.split('_')
            _class = _class.split('-')
            list_subject_name = (
                f'{subjects[_subject]}{"-" + _class[1] if len(_class) > 1 else ""}'
                if _subject in subjects else
                (
                    _class[1]
                    if len(_class) > 1 else
                    teachers.get(_teacher_login)
                )
            )
            x = '\n'.join([f'<code>{_lessons[i][1]}</code>' for i in _lessons if i == _day_code and _lessons[i][1]])
            if x:
                _render += f'<u>{list_subject_name}</u>\n{x}\n\n'
        return 0, (
            f'📙 <b>Домашнее задание</b> <i>({_day})</i>\n\n{_render}'
            if _render else f'{"<b>Нет домашнего задания</b>"} <i>({_day})</i>'
        )


router = APIRouter(
    prefix='/lycreg'
)


@router.get('/check_auth_data/')
async def check_auth_data(login: str, password: str) -> dict:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        api = LycregAPI(session)
        auth_res = await api.lycreg_authorise(login, password)

        if auth_res.get('error') is not None:
            return {'status': 400, 'error': auth_res.get('error')}
        else:
            return {'status': 200}
