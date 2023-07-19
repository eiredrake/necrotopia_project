from necrotopia.models import Grade
from necrotopia.tools import DictionaryTool


class Component:
    def __init__(self):
        self.name = ''
        self.quantity = 1
        self.mind = 0
        self.time = 0
        self.grade = Grade.Ungraded
        self.components = dict()

    @property
    def Name(self) -> str:
        return self.name

    @property
    def Quantity(self) -> int:
        return self.quantity

    @property
    def Mind(self) -> int:
        return self.mind

    @property
    def Time(self) -> int:
        return self.time

    @property
    def Components(self) -> dict:
        return self.components

    def __str__(self):
        return self.name

    def add(self, sub_component: "Component"):
        self.components[sub_component.name] = sub_component

    def collapse(self) -> {}:
        result = {}
        my_name = self.name

        for component in self.components.values():
            if len(component.components) > 0:
                sub_modules = component.collapse()
                result = DictionaryTool.mergeDictionary(result, sub_modules)
            else:
                if DictionaryTool.contains_key(component.name, result):
                    result[component.name] += component.quantity
                else:
                    result[component.name] = component.quantity

        return result

    def get_total_time(self) -> int:
        result = self.time

        for key in self.components:
            sub_component = self.components[key]
            sub_time = sub_component.get_total_time()
            result += sub_time

        return result

    def get_total_mind(self) -> int:
        result = self.mind

        for key in self.components:
            sub_component = self.components[key]
            sub_mind = sub_component.get_total_mind()
            result += sub_mind

        return result


class ComponentFactory:
    @staticmethod
    def create(quantity: int = 1, name: str = 'New', grade: Grade = Grade.Ungraded, mind: int = 0, time: int = 0) -> Component:
        result = Component()
        result.name = name
        result.grade = grade
        result.quantity = quantity
        result.mind = mind
        result.time = time

        return result
