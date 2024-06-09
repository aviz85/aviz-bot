import json

class Node:
    def __init__(self, system_prompt, required_info=None):
        self.system_prompt = system_prompt
        self.required_info = required_info or []
        self.edges = []
        self.chat_history = []  # Initialize chat_history attribute

    def add_edge(self, condition, condition_name, next_node):
        self.edges.append({"condition": condition, "condition_name": condition_name, "next_node": next_node})

    def reset_node_data(self, global_data_store):
        # Validate and reset required info based on global data store
        self.validate_required_info(global_data_store)
        self.chat_history = []  # Reset chat_history when node data is reset

    def validate_required_info(self, global_data_store):
        # Ensure required info is initialized in global data store
        for info in self.required_info:
            if info not in global_data_store:
                global_data_store[info] = None

class StateMachine:
    def __init__(self, initial_node, general_system_prompt=""):
        self.current_node = initial_node
        self.general_system_prompt = general_system_prompt  # Store the general prompt
        self.global_data_store = {}
        self.clear_global_data_store()

    def clear_global_data_store(self):
        self.global_data_store = {}
        print("Global data store has been cleared.")

    def transition_to_next_node(self):
        print(f"Current State: {self.current_node.system_prompt}")
        for edge in self.current_node.edges:
            if edge["condition"](self.global_data_store):
                print(f"Condition met for transition: {edge['condition_name']}")
                self.current_node = edge["next_node"]
                print(f"Transitioning to: {self.current_node.system_prompt}")
                self.current_node.reset_node_data(self.global_data_store)
                break
        else:
            print("No condition met for transition.")
            
CURRENT_SCENARIO = 0

class TreeBuilder:
    def __init__(self, tree_file):
        with open(tree_file, 'r') as f:
            file_content = f.read().strip()
            self.tree_data = json.loads(file_content)
            if not self.tree_data:
                raise ValueError("Loaded JSON data is empty or invalid.")

    def build_state_machine(self):
        scenario = self.tree_data["scenarios"][CURRENT_SCENARIO]
        nodes = {}
        conditions = scenario["conditions"]
        general_system_prompt = scenario.get("general_system_prompt", "")  # Retrieve the general system prompt

        # Define nodes
        for node_data in scenario["nodes"]:
            node = Node(
                system_prompt=node_data["system_prompt"],
                required_info=node_data.get("required_info", [])
            )
            nodes[node_data["name"]] = node

        # Connect nodes with edges
        for node_data in scenario["nodes"]:
            node = nodes[node_data["name"]]
            for edge in node_data["edges"]:
                condition = eval(conditions[edge["condition"]])  # Evaluate the condition
                next_node = nodes[edge["next_node"]]
                node.add_edge(condition, edge["condition"], next_node)

        # Initialize the state machine with the starting node and the general prompt
        state_machine = StateMachine(nodes["opening_node"], general_system_prompt)
        return state_machine