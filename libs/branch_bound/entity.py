from abc import ABC, abstractmethod
from typing import Iterable

class Entity(ABC):
    """
    Абстрактный класс «Сущность», определяющий интерфейс узла
    для метода ветвей и границ.
    """

    @abstractmethod
    def isComplete(self) -> bool:
        """
        Возвращает True, если данный узел представляет полное допустимое решение.
        """
        ...

    @abstractmethod
    def branches(self) -> Iterable['Entity']:
        """
        Ветвление: возвращает итерируемый объект дочерних узлов (состояний).
        """
        ...

    @abstractmethod
    def pack(self) -> int:
        """
        Кодирует объект
        """
        ...

    @abstractmethod
    def unpack(self, code: int):
        """
        Декодирует объект
        """
        ...

    @abstractmethod
    def isCorrect(self) -> bool:
        """
        Дополнительное фильтрация
        """
        ...

    def isSuitable(self) -> bool:
        """
        Сущность подходит
        """
        ...

