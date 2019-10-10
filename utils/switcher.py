from typing import Any, Callable, Dict

Action = Callable[[], Any]
Case = Callable[[], bool]


class Switcher:
    __cases: Dict[Any, Action] = {}
    __default: Action = None

    def case(self, case: Case, action: Action) -> None:
        if not callable(action):
            raise ValueError("Action must be callable")
        if not callable(case):
            raise ValueError("case must be callable")
        self.__cases[case] = action

    def default(self, action: Action):
        if action is not None and not callable(action):
            raise ValueError("Default action must be callable")

        self.__default = action

    def exec(self):
        for case in self.__cases:
            if case():
                return self.__cases.get(case)()

        if self.__default is not None:
            return self.__default()
        return None

    @staticmethod
    def from_dict(cases: Dict[Any, Action], default: Action = None):
        switcher = Switcher()
        switcher.default(default)

        for case in cases.keys():
            switcher.case(case, cases.get(case))
        return switcher
