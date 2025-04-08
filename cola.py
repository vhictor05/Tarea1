class ColaMisiones:
    def __init__(self):
        self.items = []

    def enqueue(self, mission):
        self.items.append(mission)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)

    def first(self):
        if not self.is_empty():
            return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
