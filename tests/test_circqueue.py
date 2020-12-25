from utils import CircQueue


def test_circQueue():
    #__GIEVN__
    q = CircQueue()
    for i in range(q.max_size):
        q.put([i * 10])

    assert len(q.queue) == 10
    actual = [q.get_with_index() for i in range(q.max_size)]
    expected = [ (i, [i*10]) for i in range(10)]
    assert actual == expected
    assert q.get_current_read_pointer() == 0
    assert q.get_current_put_pointer() == 0

def test_has_data():
    q = CircQueue()

    for i in range(5):
        q.put([f'Next_{i}'])

    assert q.has_data_for_index(0)
    assert not q.has_data_for_index(8)

    assert q.get() == ['Next_0']
    assert q.get() == ['Next_1']
