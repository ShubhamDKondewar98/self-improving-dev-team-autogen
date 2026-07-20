class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

c = Counter()
bound = c.increment   # NOT calling it — just grabbing a reference to the method

print(bound.__self__ is c)   # True
print(bound.__self__.count)  # 0 — same as c.count