def real_id_to_upb_id(real_id):
    ids = real_id.split('.')
    return int(ids[0]), int(ids[1])

def upb_id_to_real_id(network_id, device_id):
    return '{0}.{1}'.format(network_id, device_id)

def check_real_id(real_id):
    if type(real_id) is not str:
        return False
    try:
        net, dest = real_id_to_upb_id(real_id)
        if 0 <= net < 256 and 0 <= dest < 256:
            return True
        else:
            return False

    except (ValueError, IndexError):
        return False
