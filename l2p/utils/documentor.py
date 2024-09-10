import os, datetime, json, logging

class DocumentClass:
    def __init__(self):
        self.initiate_flag = False
        
        # Set up the logger
        self.logger = logging.getLogger("LLM Planner")
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(message)s')
        self.log_file = None
        self.handler = None
    
    def initiate(self, domain, results_dir, **kwargs):
        self.initiate_flag = True
        self.results_dir = results_dir
        self.domain = domain
        self.directory = os.path.join(self.results_dir, self.domain, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        
        os.makedirs(self.directory, exist_ok=True)  # Create directory if it doesn't exist
        
        # Update info_file path to be within the new directory
        # info file contains static information and parameters of the domain
        self.info_file = os.path.join(self.directory, "info.txt")
        
        with open(self.info_file, "w") as file:
            file.write(f"Domain: {domain}\n\n")
            file.write(f"Time: {datetime.datetime.now()}\n\n")
            for k, v in kwargs.items():
                file.write(f"{k}: {v}\n\n")
        
        # Set up logger to write to a file in the new directory
        # log file records generated messages during execution
        self.log_file = os.path.join(self.directory, "logfile.log")
        if self.handler:
            self.logger.removeHandler(self.handler)
        self.handler = logging.FileHandler(self.log_file)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
                
    def document(self, *messages, sep: str = '', subsection: bool=True):
        # Get the current timestamp
        timestamp = datetime.datetime.now()
        
        # Combine all messages into a single string
        combined_message = sep.join([str(m) for m in messages])
        
        # Prepend the timestamp to the combined message
        message = f"{timestamp}\n\n{combined_message}"
        
        # Add subsection formatting if needed
        if subsection:
            message = f"{'-'*100}\n{message}\n{'-'*100}"
        
        # Output the message
        if not self.initiate_flag:
            print(message)
        else:
            self.logger.debug(message)
            
Documentor = DocumentClass()
        
# Example usage
if __name__ == "__main__":
    results_dir = "tests/results"
    domain = "Blocksworld"
    
    Documentor.initiate(
        results_dir=results_dir,
        domain=domain, 
        domain_description="Blocksworld is ...",
        engine="OpenAI",
        model="gpt-4o-mini"
        )

    Documentor.document("This is a message.")
    Documentor.document("Hi this happened.")
    Documentor.document("And then this happened.")