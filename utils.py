from typing import Tuple, List


class CircQueue:
    def __init__(self):
        self.counter = 0
        self.max_size = 10
        self.queue = [None for i in range(self.max_size)]
        self._read_ptr: int = 0
        self._put_ptr: int = 0

    def get(self) -> Tuple[int, List]:
        return self.get_with_index()[1]

    def get_before(self, before: int):
        i = self._put_ptr - before
        if i < 0 :
            i = self._put_ptr + self.max_size - before
        return self.queue[i]


    def get_with_index(self) -> Tuple[int, List]:
        i = self._read_ptr
        self._read_ptr += 1
        if self._read_ptr >= self.max_size:
            self._read_ptr = 0

        return i, self.queue[i]


    def get_current_read_pointer(self):
        return self._read_ptr

    def get_current_put_pointer(self):
        return self._put_ptr


    def put(self, data):
        i = self._put_ptr
        self._put_ptr += 1
        if self._put_ptr >= self.max_size:
            self._put_ptr = 0
        return self.put_with_index(i, data)

    def put_with_index(self, index: int, data):
        self.counter +=1
        self.queue[index] = data

    def has_data_for_index(self, index: int):
        return self.counter >= index
