"""
The model service represents the physical devices connected to the bridge
"""


def create_actuple(service, method, *args, **kwargs):
    return service, [method] + list(args), kwargs
