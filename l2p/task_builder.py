class Task_Builder:
    def __init__(self, domain, objects, initial, goal):
        self.domain=domain
        self.objects=objects
        self.initial=initial
        self.goal=goal

    def extract_initial_state(model, prompt):
        response = model.get_response(prompt)
        print(response.strip())

    def extract_goal_state():
        pass

    def extract_objects():
        pass

    def generate_task():
        pass

if __name__ == "__main__":
    
    task = Task_Builder()
    description = "The AI agent here is a mechanical robot arm that can pick and place the blocks. Only one block may be moved at a time: it may either be placed on the table or placed atop another block. Because of this, any blocks that are, at a given time, under another block cannot be moved."
    
    print(task.extract_initial_state("GPT-3.5-Turbo", description))