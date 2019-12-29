def find_in_list(elements, predicate):
    for el in elements:
        if predicate(el):
            return el
    return None


def resize(list_, size, filling=None):
    if size > len(list_):
        list_.extend([filling for _ in range(len(list_), size)])
    else:
        del list_[size:]
