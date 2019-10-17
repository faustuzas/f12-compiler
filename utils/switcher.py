from typing import Any, Callable, Dict, Union, List, Tuple
from enum import Enum
from collections.abc import Iterable

Action = Callable[[Any], Any]
Case = Union[str, int, float, List, Tuple, Enum]


class Switcher:
    __cases: Dict[Case, Action]
    __default: Action

    def __init__(self) -> None:
        self.__cases = {}

    def case(self, case: Case, action: Action) -> None:
        if not callable(action):
            raise ValueError("Action must be callable")
        self.__cases[case] = action

    def default(self, action: Action):
        if action is not None and not callable(action):
            raise ValueError("Default action must be callable")
        self.__default = action
        return self

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


class FasterSwitcher:
    __ascii_actions: List[Union[Action, None]]
    __others_cases: Dict[Any, Action]
    __default: Union[Action, None]

    def __init__(self):
        self.__ascii_actions = [None] * 256
        self.__others_cases = {}
        self.__default = None

    def case(self, case: Union[Iterable, int], action: Action) -> None:
        if not callable(action):
            raise ValueError("Action must be callable")

        if isinstance(case, int):
            str_int = str(case)
            if len(str_int) != 1:
                raise ValueError("Integer has to be single digit")
            self.__ascii_actions[ord(str_int)] = action
            return

        if isinstance(case, Iterable):
            for c in case:
                if isinstance(c, str) and len(c) == 1:
                    self.__ascii_actions[ord(c)] = action
                else:
                    self.__others_cases[c] = action
            return

        self.__others_cases[case] = action

    def default(self, action: Action):
        if action is not None and not callable(action):
            raise ValueError("Default action must be callable")
        self.__default = action
        return self

    def exec(self, ctx, value):
        if isinstance(value, int):
            str_int = str(value)
            if len(str_int) != 1:
                raise ValueError("Integer has to be single digit")
            action = self.__ascii_actions[ord(str_int)]
            if action is not None:
                return action(ctx)

        if isinstance(value, str) and len(value) == 1:
            action = self.__ascii_actions[ord(value)]
        else:
            action = self.__others_cases[value]

        if action is not None:
            return action(ctx)

        if self.__default is not None:
            return self.__default(ctx)
            
        return None

    @staticmethod
    def from_dict(cases: Dict[Iterable, Action], default: Action = None):
        switcher = FasterSwitcher()
        switcher.default(default)

        for case in cases.keys():
            switcher.case(case, cases.get(case))
        return switcher
