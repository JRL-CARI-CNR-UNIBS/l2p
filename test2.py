def dict_list_to_string(dict_list):
    # Start the string with "(AND "
    result_str = "(AND \n"

    # Loop through each dictionary in the list
    for item in dict_list:
        # Extract the name and parameters from the dictionary
        name = item['name']
        params = " ".join(item['params'])
        
        # Append the predicate in the desired format
        result_str += f"   ({name} {params}) \n"

    # Close the string with ")"
    result_str += ")"

    return result_str

# Example usage
dict_list = [
    {'name': 'on', 'params': ['red_block', 'green_block']},
    {'name': 'clear', 'params': ['green_block']},
    {'name': 'clear', 'params': ['red_block']}
]

result = dict_list_to_string(dict_list)
print(result)
