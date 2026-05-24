from queue import SimpleQueue
from .entity import Entity

class BranchAndBound:
    """
    Обобщённый решатель методом ветвей и границ.
    """

    def __init__(self, initial: Entity, verbose = False):
        """
        Параметры
        ---------
        initial : Entity
            Начальный узел (корень дерева перебора).
        """
        self.initial = initial
        self.verbose = verbose
        self.entities = set()

    def solve(self):
        queue = SimpleQueue[Entity]()
        queue.put(self.initial)
        i = 0
        while not queue.empty():
            entity = queue.get()
            if self.verbose:
                print(f"{i}. {entity}")
                i += 1

            if entity.isComplete():
                if entity.isSuitable():
                    h = entity.pack()
                    if h not in self.entities:
                        self.entities.add(h)
                continue

            for child in entity.branches():
                if child.isCorrect():
                    queue.put(child)
        return self.entities

    def save_if(self, filename, pred):
        with open(filename, "w") as f:
            f.writelines([f"{num}\n" for num in self.entities if pred(num)])

    def save_transform(self, filename, frans):
        with open(filename, "w") as f:
            f.writelines([f"{frans(num)}\n" for num in self.entities])

    def save(self, filename):
        return self.save_if(filename, lambda x: True)

