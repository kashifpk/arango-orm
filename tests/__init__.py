import logging

log = logging.getLogger(__name__)



def all_in(keys, collection) -> bool:
    "Assert that all given keys are present in the given collection, dict, list or tuple"

    for key in keys:
        if key not in collection:
            return False

    return True


def any_in(keys, collection) -> bool:
    "Assert that any of the given keys is present in the given collection, dict, list or tuple"

    for key in keys:
        if key in collection:
            return True

    raise False


def none_in(keys, collection) -> bool:
    "Assert that none of the given keys is present in the given collection, dict, list or tuple"

    for key in keys:
        if key in collection:
            return False

    return True


def has_same_items(left, right) -> bool:
    if not set(left) == set(right):
        return False
    return True


def verify_property_values(obj, **kwargs) -> bool:
    "Verify that properties (keys in kwargs) exist and contain correct value (values in kwargs)"

    for k, v in kwargs.items():
        if hasattr(obj, k) is False:
            log.debug(f"Property {k} not present")
            return False

        if getattr(obj, k) != v:
            log.debug(f"Property {k} value incorrect. {getattr(obj, k)}!={v}")
            return False

    return True
