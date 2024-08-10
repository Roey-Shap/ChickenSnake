def get_user_input(string_validity_check_func, input_prompt: str) -> str | None:
    user_input_valid: bool = False
    current_input = None
    while not user_input_valid:
        current_input = input(input_prompt)
        user_input_valid = string_validity_check_func(current_input)
        if not user_input_valid:
            print("Invalid input.")
    
    return current_input

def yes_no_input_check(input_string: str) -> bool:
    return input_string.lower() in ["y", "n", "yes", "no"]