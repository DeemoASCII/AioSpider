# coding=utf-8
from aleph.utils import loc_dict, resolve_address

_direct_cities = ['11', '12', '31', '50']


def _load_locations():
    id_names = {}
    for k in loc_dict:
        for lid in loc_dict[k]:
            id_names[str(lid)] = k

    loc_details = {}
    for lid, lname in id_names.items():
        is_direct = lid[:2] in _direct_cities
        if lid.endswith('0000'):
            prov, city, county = lname, '', ''
        elif lid.endswith('00'):
            prov_id = lid[:2] + '0000'
            prov = id_names[prov_id]
            city = prov if is_direct else lname
            county = ''
        else:
            prov_id = lid[:2] + '0000'
            prov = id_names[prov_id]

            city_id = lid[:4] + '00'
            if is_direct:
                city = prov
            elif city_id in id_names:
                city = id_names[city_id]
            else:
                city = lname

            county = lname

        loc_details[int(lid)] = (int(lid), prov, city, county)
    return loc_details


locations = _load_locations()


def normalize(loc):
    # TODO: if the 'loc' is english
    loc_id = resolve_address(loc)
    if loc_id:
        return locations[loc_id]
    return None


def normalize_loc(loc):
    if not loc:
        return None
    loc = loc.lstrip(' :').strip()
    norm = normalize(loc)
    if norm:
        loc_id, province, city, county = norm
        return {'id': loc_id, 'province': province, 'city': city, 'county': county}


def normalize_locs(locs):
    normalized_locs = []
    locs_found = set()
    for loc in locs:
        norm = normalize(loc)
        if norm:
            loc_id, province, city, county = norm
            if loc_id not in locs_found:
                normalized_locs.append({'id': loc_id, 'province': province, 'city': city, 'county': county})
                locs_found.add(loc_id)

    return normalized_locs


if __name__ == '__main__':
    print(normalize('上海'))
    print(normalize('上海城区'))
    print(normalize('上海市静安区'))
    print(normalize('苏州市姑苏区'))
    print(normalize('江苏'))
