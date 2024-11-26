import unittest
from l2p.task_builder import TaskBuilder
from l2p.utils.pddl_parser import *
from .mock_llm import MockLLM 

class TestTaskBuilder(unittest.TestCase):
    def setUp(self):
        self.domain_builder = TaskBuilder()
        self.domain_desc = 'Blocksworld is...'
    
    def test_extract_objects(self):
        pass
        
    def test_extract_initial_state(self):
        pass
        
    def test_extract_object_state(self):
        pass
        
    def test_extract_task(self):
        pass
        
    def test_extract_nl_conditions(self):
        pass
        
    def test_generate_task(self):
        pass
        
    def test_format_action(self):
        pass
        
    def test_format_objects(self):
        pass
        
    def test_format_initial(self):
        pass
        
    def test_format_goal(self):
        pass

if __name__ == "__main__":
    unittest.main()