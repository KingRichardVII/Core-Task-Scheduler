#Richard Phan
#COMP 282
#11/26/25

#Program details - see README file.

import sys

#task = job that requires computer attention
class Task:
    #remaining time = how much time task still needs to finish
    #insertion_order - determines which task goes first in tie
    __slots__ = ("id", "priority", "remaining", "insertion_order")

    def __init__(self, id_: str, priority: int, remaining: int,
                 insertion_order: int = 0):
        self.id = id_
        self.priority = priority
        self.remaining = remaining
        self.insertion_order = insertion_order

#Vector analogy = magic toybox that doubles when full
#Use to store items for heap
class Vector:
    def __init__(self, cap: int = 4):
        self._data = [None] * cap
        self._size = 0
        self._capacity = cap

    def size(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def get(self, index: int):
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        return self._data[index]

    def set(self, index: int, value):
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        self._data[index] = value
    #add to end of vector
    #if vector full, makes bigger first
    def push_back(self, value):
        if self._size == self._capacity:
            self._grow()
        self._data[self._size] = value
        self._size += 1

    #takes last item out of vector
    def pop_back(self):
        if self._size == 0:
            raise IndexError("Cannot pop from empty vector")
        self._size -= 1
        value = self._data[self._size]
        self._data[self._size] = None
        return value

    def swap(self, i: int, j: int):
        temp = self._data[i]
        self._data[i] = self._data[j]
        self._data[j] = temp

    #makes vector double
    def _grow(self):
        self._capacity *= 2
        new_data = [None] * self._capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data

#used to determine which task to run next/priority
class MinHeap:
    def __init__(self):
        self._array = Vector()
        self._insertion_counter = 0

    def is_empty(self):
        return self._array.is_empty()

    def size(self):
        return self._array.size()

    #add task to heap
    #give insertion_order to remember when it joined
    def insert(self, task: Task):
        # assign insertion order when task enters READY
        task.insertion_order = self._insertion_counter
        self._insertion_counter += 1
        self._array.push_back(task)
        self._bubble_up(self._array.size() - 1)

    def extract_min(self):
        if self.is_empty(): #check if empty
            return None

        min_task = self._array.get(0)
        last_task = self._array.pop_back()

        if not self.is_empty():
            self._array.set(0, last_task)
            self._bubble_down(0)

        return min_task

    def peek(self):
        if self.is_empty():
            return None
        return self._array.get(0)

    #return task in same order they would run (without changing) real heap
    def get_all_sorted(self):
        result = []
        temp_heap = MinHeap()

        # Insert CLONES of tasks into a temp heap
        # so we don't mutate insertion_order of the originals.
        for i in range(self._array.size()):
            task = self._array.get(i)
            clone = Task(task.id, task.priority, task.remaining,
                         task.insertion_order)
            temp_heap.insert(clone)

        while not temp_heap.is_empty():
            result.append(temp_heap.extract_min())

        return result

    def _bubble_up(self, index: int):
        while index > 0:
            parent = (index - 1) // 2
            if self._compare(self._array.get(index),
                             self._array.get(parent)) < 0:
                self._array.swap(index, parent)
                index = parent
            else:
                break

    def _bubble_down(self, index: int):
        size = self._array.size()
        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self._compare(self._array.get(left),
                                             self._array.get(smallest)) < 0:
                smallest = left

            if right < size and self._compare(self._array.get(right),
                                              self._array.get(smallest)) < 0:
                smallest = right

            if smallest != index:
                self._array.swap(index, smallest)
                index = smallest
            else:
                break
    #compare two tasks by priority
    #if equal, compare by who joined first
    def _compare(self, task1: Task, task2: Task):
        if task1.priority != task2.priority:
            return task1.priority - task2.priority
        # Tie-breaker: earlier insertion order
        return task1.insertion_order - task2.insertion_order

#FIFO queue for blocked tasks
class TaskQueue:
    def __init__(self, cap: int = 4):
        self._data = [None] * cap
        self._capacity = cap
        self._head = 0
        self._tail = 0
        self._size = 0

    def is_empty(self):
        return self._size == 0

    def size(self):
        return self._size

    #insert at tail
    def enqueue(self, task: Task):
        if self._size == self._capacity:
            self._grow()

        self._data[self._tail] = task
        self._tail = (self._tail + 1) % self._capacity
        self._size += 1
    #delete at head
    def dequeue(self):
        if self.is_empty():
            return None

        task = self._data[self._head]
        self._data[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        return task

    #return blocked tasks in order
    #DOES NOT touch real queue
    def get_all(self):
        result = []
        index = self._head
        for _ in range(self._size):
            result.append(self._data[index])
            index = (index + 1) % self._capacity
        return result

    #expand if full
    def _grow(self):
        new_capacity = self._capacity * 2
        new_data = [None] * new_capacity

        index = self._head
        for i in range(self._size):
            new_data[i] = self._data[index]
            index = (index + 1) % self._capacity

        self._data = new_data
        self._capacity = new_capacity
        self._head = 0
        self._tail = self._size

#manages READY, BLOCKED, RUNNING tasks
#commands from input file tell schedule what to do next
class Scheduler:
    def __init__(self):
        self.ready = MinHeap()
        self.blocked = TaskQueue()
        self.running = None

    #look for a task in running, ready or blocked
    def _task_exists(self, task_id: str) -> bool:
        # Check RUNNING
        if self.running is not None and self.running.id == task_id:
            return True

        # Check READY heap
        for i in range(self.ready._array.size()):
            task = self.ready._array.get(i)
            if task is not None and task.id == task_id:
                return True

        # Check BLOCKED queue
        index = self.blocked._head
        for _ in range(self.blocked._size):
            task = self.blocked._data[index]
            if task is not None and task.id == task_id:
                return True
            index = (index + 1) % self.blocked._capacity

        return False

    def add_task(self, args):
        if len(args) != 3:
            print(
                "ERROR: ADD_TASK requires 3 arguments: id priority burst_time")
            return

        task_id = args[0]

        try:
            priority = int(args[1])
            burst_time = int(args[2])
        except ValueError:
            print("ERROR: priority and burst_time must be integers")
            return

        if burst_time <= 0:
            print("ERROR: burst_time must be a positive integer")
            return

        # make sure we're not adding the same thing
        if self._task_exists(task_id):
            print("DUPLICATE")
            return

        task = Task(task_id, priority, burst_time)
        self.ready.insert(task)

    def tick(self):
        # If no running task, try to schedule one
        if self.running is None:
            if not self.ready.is_empty():
                self.running = self.ready.extract_min()

        # If there's a running task, execute it
        if self.running is not None:
            print(f"RUNNING {self.running.id}")
            self.running.remaining -= 1

            if self.running.remaining == 0:
                # Task finished: remove from system
                self.running = None
        else:
            print("IDLE")

    def block(self):
        if self.running is None:
            print("ERROR: NO_TASK_RUNNING")
            return

        print(f"BLOCKED {self.running.id}")
        self.blocked.enqueue(self.running)
        self.running = None

    def unblock(self):
        if self.blocked.is_empty():
            print("ERROR: NO_TASK_BLOCKED")
            return

        task = self.blocked.dequeue()
        print(f"UNBLOCKED {task.id}")
        self.ready.insert(task)

    def print_ready(self):
        print("READY_QUEUE")
        if self.ready.is_empty():
            print("EMPTY")
        else:
            tasks = self.ready.get_all_sorted()
            for task in tasks:
                print(
                    f"-> {task.id} | priority={task.priority} | remaining="
                    f" {task.remaining}")

    def print_blocked(self):
        print("BLOCKED_QUEUE")
        if self.blocked.is_empty():
            print("EMPTY")
        else:
            tasks = self.blocked.get_all()
            for task in tasks:
                print(f"-> {task.id} | remaining={task.remaining}")

    def status(self):
        print("STATUS")
        if self.running is None:
            print("IDLE")
        else:
            print(
                f"-> {self.running.id} | priority={self.running.priority} |  "
                f"remaining={self.running.remaining}"
            )


def parse_line(line: str):
    #Parse a command line, handling quoted strings.
    line = line.strip()

    if not line or line.startswith('#'):
        return None

    tokens = []
    current = []
    in_quotes = False

    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ' ' and not in_quotes:
            if current:
                tokens.append(''.join(current))
                current = []
        else:
            current.append(char)

    if current:
        tokens.append(''.join(current))

    return tokens

#main:
#ensure we got a valid file name
#read commands from file
#tells schedule what to do for each command
def main():
    if len(sys.argv) != 2:
        print("USAGE: <program> <commands_file>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except (FileNotFoundError, IOError):
        print("USAGE: <program> <commands_file>")
        sys.exit(1)

    scheduler = Scheduler()

    for line in lines:
        tokens = parse_line(line)

        if tokens is None:
            continue

        if not tokens:
            continue

        command = tokens[0].upper()
        args = tokens[1:]

        if command == "ADD_TASK":
            scheduler.add_task(args)
        elif command == "TICK":
            scheduler.tick()
        elif command == "BLOCK":
            scheduler.block()
        elif command == "UNBLOCK":
            scheduler.unblock()
        elif command == "PRINT_READY":
            scheduler.print_ready()
        elif command == "PRINT_BLOCKED":
            scheduler.print_blocked()
        elif command == "STATUS":
            scheduler.status()
        elif command == "QUIT":
            break
        else:
            print(f"ERROR: Unknown command '{command}'")


if __name__ == "__main__":
    main()