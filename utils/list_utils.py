def find_in_list(elements, predicate):
    for el in elements:
        if predicate(el):
            return el
    return None
