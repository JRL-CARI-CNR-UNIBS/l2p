from typing import Dict

def delete_key_from_dict(d: Dict[str, str], key_to_delete: str) -> Dict[str, str]:
    """
    Removes the specified key from the dictionary if it exists.

    :param d: The dictionary from which the key should be removed.
    :param key_to_delete: The key to remove from the dictionary.
    :return: A new dictionary with the specified key removed.
    """
    # Create a new dictionary excluding the key to delete
    return {k: v for k, v in d.items() if k != key_to_delete}

# Example usage:
my_dict = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
}

# Delete the key "key2"
updated_dict = delete_key_from_dict(my_dict, "key2")
print(updated_dict)
