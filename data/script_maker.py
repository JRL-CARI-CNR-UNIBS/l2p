from jinja2 import Environment, FileSystemLoader
import os

def generate():
    while True:
        user_input = input("Enter 'exit' to finish, or enter anything to continue: ")
        if user_input == 'exit':
            break
        else:
            generate_domain_files()

def generate_domain_files():

    script_dir = os.path.dirname(os.path.realpath(__file__)) # get path of current script
    save_folder = os.path.join(script_dir, "scripts")

    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("domain_prompt.txt")

    domain_variables = [
        {"domain_name": "Blocksworld", "description": "robot in a world where there are a set of blocks that can be stacked on top of each other, an arm that can hold one block at a time, and a table where blocks can be placed.", "actions": "pickup, putdown, stack, and unstack"},
        {"domain_name": "Barman", "description": "barman that manipulates drink dispensers, shot glasses and a shaker. You have two hands.", "goal":"serves a desired set of drinks", "actions": "Grasp, Leave, Fill, Refill, Empty, Clean, Pour, Shake"},
    ]

    for d in domain_variables:
        filename = f"message_{d['domain_name'].lower()}.txt"
        file_path = os.path.join(save_folder, filename)
        content = template.render(
            d
        )
        with open(file_path, mode="w", encoding="utf-8") as message:
            message.write(content)
            print(f"... wrote {file_path}")

def generate_problem_files():
    pass

if __name__ == "__main__":
    generate()