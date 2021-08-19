import json


def generate_ids(starting_number, count):
    ids = []
    s = []
    for i in range(count):
        base_id = i + starting_number
        a = (base_id % 9) * 17
        b = (base_id % 13) * 315
        transformed_id = base_id * a + b
        s.append(transformed_id)
        ids.append({"id": transformed_id})

    assert len(s) == len(set(s))
    return ids


from_num = 2
count = 100
ids = []
l = generate_ids(from_num, count)
with open('attrib.json', 'w') as outfile:
    json.dump(l, outfile)
