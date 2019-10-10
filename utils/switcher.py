from typing import Any, Callable, Dict, Union, List, Tuple
from collections.abc import Iterable

Action = Callable[[], Any]
Case = Union[str, int, float, List, Tuple]


class Switcher:
    __cases: Dict[Case, Action] = {}
    __default: Action = None

    def case(self, case: Case, action: Action) -> None:
        if not callable(action):
            raise ValueError("Action must be callable")
        self.__cases[case] = action

    def default(self, action: Action):
        if action is not None and not callable(action):
            raise ValueError("Default action must be callable")

        self.__default = action

    def exec(self, value):
        for case in self.__cases:
            if self.__check_case(case, value):
                return self.__cases.get(case)()

        if self.__default is not None:
            return self.__default()
        return None

    @staticmethod
    def __check_case(case: Case, value):
        if isinstance(case, str):
            return case == value

        if isinstance(case, Iterable):
            return value in case

        return case == value

    @staticmethod
    def from_dict(cases: Dict[Case, Action], default: Action = None):
        switcher = Switcher()
        switcher.default(default)

        for case in cases.keys():
            switcher.case(case, cases.get(case))
        return switcher

