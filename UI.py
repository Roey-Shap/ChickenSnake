from contextlib import redirect_stdout
import metadata

def log_to_file(text):
    with open(metadata.current_execution_log_filepath, 'a') as f:
        with redirect_stdout(f):
            print(text)

def log_and_print(text: str="", do_print=True):
    if do_print:
        print(text)
    # Very wasteful to do it like this but it's safe and I don't care!!! :)
    log_to_file(text)

def get_user_input(string_validity_check_func, input_prompt: str) -> str | None:
    user_input_valid: bool = False
    current_input = None
    while not user_input_valid:
        current_input = input(input_prompt)
        user_input_valid = string_validity_check_func(current_input)
        if not user_input_valid:
            log_and_print("Invalid input.")
    
    return current_input

def yes_no_input_check(input_string: str) -> bool:
    return input_string.lower() in ["y", "n", "yes", "no"]