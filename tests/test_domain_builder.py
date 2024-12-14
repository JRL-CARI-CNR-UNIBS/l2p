import unittest
from l2p.domain_builder import DomainBuilder
from l2p.utils.pddl_parser import *
from .mock_llm import MockLLM


class TestDomainBuilder(unittest.TestCase):
    def setUp(self):
        self.domain_builder = DomainBuilder()
        self.domain_desc = "Blocksworld is..."
        self.prompt_template = "Domain: {domain_desc}\nTypes: {types}"
        self.types = None

    def test_extract_type(self):
        mock_llm_1 = MockLLM(['{"robot": "A machine capable of carrying out tasks."}'])
        mock_llm_2 = MockLLM(["This is not a valid dictionary format."])
        mock_llm_3 = MockLLM([None])

        types, llm_response = self.domain_builder.extract_type(
            model=mock_llm_1,
            domain_desc=self.domain_desc,
            prompt_template=self.prompt_template,
            types=self.types,
        )
        self.assertEqual(types, {"robot": "A machine capable of carrying out tasks."})
        self.assertEqual(
            llm_response, '{"robot": "A machine capable of carrying out tasks."}'
        )

        with self.assertRaises(RuntimeError) as context:
            types, llm_response = self.domain_builder.extract_type(
                model=mock_llm_2,
                domain_desc=self.domain_desc,
                prompt_template=self.prompt_template,
                types=self.types,
            )
        self.assertIn("Max retries exceeded", str(context.exception))

        with self.assertRaises(RuntimeError) as context:
            types, llm_response = self.domain_builder.extract_type(
                model=mock_llm_3,
                domain_desc=self.domain_desc,
                prompt_template=self.prompt_template,
                types=self.types,
            )
        self.assertIn("Max retries exceeded", str(context.exception))

    def test_extract_type_hierarchy(self):
        mock_model = MockLLM(["{'car': 'vehicle', 'truck': 'vehicle'}"])

        domain_desc = "A domain about vehicles"
        prompt_template = "Extract types from: {domain_desc}. Current types: {types}."
        types = {"bike": "vehicle"}

        expected_hierarchy = {"car": "vehicle", "truck": "vehicle"}
        expected_response = "{'car': 'vehicle', 'truck': 'vehicle'}"

        result, response = self.domain_builder.extract_type_hierarchy(
            model=mock_model,
            domain_desc=domain_desc,
            prompt_template=prompt_template,
            types=types,
        )

        self.assertEqual(result, expected_hierarchy)
        self.assertEqual(response, expected_response)

    def test_extract_nl_actions(self):
        mock_model = MockLLM(
            ["{'drive': 'Move a vehicle', 'park': 'Stop a vehicle at a location'}"]
        )

        domain_desc = "Vehicle domain"
        prompt_template = "Extract actions for: {domain_desc}. Current actions: {nl_actions}. Current types: {types}."
        nl_actions = {"start": "Initiate a vehicle"}
        types = {"car": "vehicle"}

        expected_actions = {
            "drive": "Move a vehicle",
            "park": "Stop a vehicle at a location",
        }
        expected_response = (
            "{'drive': 'Move a vehicle', 'park': 'Stop a vehicle at a location'}"
        )

        result, response = self.domain_builder.extract_nl_actions(
            model=mock_model,
            domain_desc=domain_desc,
            prompt_template=prompt_template,
            nl_actions=nl_actions,
            types=types,
        )

        self.assertEqual(result, expected_actions)
        self.assertEqual(response, expected_response)

    def test_pddl_action(self):
        self.maxDiff = None
        llm_response = """
        ### Action Parameters
        ```
        - ?v - vehicle: The vehicle travelling
        - ?from - location: The location travelling from
        - ?to - location: The location travelling to
        ```

        ### Action Preconditions
        ```
        (and
            (at ?v ?from) ; The vehicle is at the starting location
            (or (connected ?from ?to) (connected ?to ?from)) ; A road exists between the locations
        )
        ```

        ### Action Effects
        ```
        (and
            (not (at ?v ?from)) ; ?v is no longer at ?from
            (at ?v ?to) ; ?v is now instead at ?to
        )
        ```

        ### New Predicates
        ```
        - (at ?o - object ?l - location): true if the object ?o (a vehicle or a worker) is at the location ?l
        - (connected ?l1 - location ?l2 - location): true if a road exists between ?l1 and ?l2 allowing vehicle travel between them.
        ``` 
        """
        mock_model = MockLLM([llm_response])

        domain_desc = "Vehicle domain"
        prompt_template = "Extract PDDL action for: {domain_desc}. Action: {action_name} with description {action_desc}."
        action_name = "drive"
        action_desc = "Move a vehicle between locations."
        action_list = {"park": "Stop a vehicle"}
        types = {"car": "vehicle"}
        predicates = [
            {
                "name": "at",
                "desc": "true if the object ?o (a vehicle or a worker) is at the location ?l",
                "parameters": ["?o - object", "?l - location"],
            },
            {
                "name": "connected",
                "desc": "true if a road exists between ?l1 and ?l2 allowing vehicle travel between them.",
                "parameters": ["?l1 - location", "?l2 - location"],
            },
        ]

        expected_predicates = predicates
        expected_response = llm_response

        action, new_preds, response = self.domain_builder.extract_pddl_action(
            model=mock_model,
            domain_desc=domain_desc,
            prompt_template=prompt_template,
            action_name=action_name,
            action_desc=action_desc,
            action_list=action_list,
            predicates=predicates,
            types=types,
        )

        # TODO: finish this comparing actual Action type to this response.

        print("\n", action)
        print("\n", new_preds)

    def test_extract_pddl_actions(self):
        pass

    def test_extract_parameters(self):
        pass

    def test_extract_preconditions(self):
        pass

    def test_extract_effects(self):
        pass

    def test_extract_predicates(self):
        pass

    def test_generate_domain(self):
        pass


if __name__ == "__main__":
    unittest.main()
