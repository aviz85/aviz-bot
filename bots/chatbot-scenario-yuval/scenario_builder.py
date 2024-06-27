import json

class Agent:
    def __init__(self, llm, system_prompt, goal, conditions, tools):
        self.llm = llm
        self.system_prompt = system_prompt
        self.goal = goal
        self.conditions = conditions
        self.tools = tools
        self.chat_history = []

    def add_condition(self, condition, next_agent_id):
        self.conditions.append({"condition": condition, "next_agent_id": next_agent_id})

    def reset_agent_data(self, global_data_store):
        self.chat_history = []
        # Reset other agent-specific data if needed

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
    def __init__(self, initial_agent, agents, general_system_prompt=""):
        self.current_agent = initial_agent
        self.general_system_prompt = general_system_prompt
        self.global_data_store = {}
        self.agents = agents
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
        agents = {}
        conditions = scenario["conditions"]
        general_system_prompt = scenario.get("general_system_prompt", "")

        # Define agents
        for agent_data in scenario["agents"]:
            llm = agent_data["llm"]
            system_prompt = agent_data["system_prompt"]
            goal = agent_data["goal"]
            tools = agent_data.get("tools", [])
            agent = Agent(
                llm=llm,
                system_prompt=system_prompt,
                goal=goal,
                conditions=[],
                tools=tools
            )
            agents[agent_data["id"]] = agent

        # Connect agents with conditions
        for agent_data in scenario["agents"]:
            agent = agents[agent_data["id"]]
            for condition in agent_data["conditions"]:
                condition_func = eval(conditions[condition["condition"]])
                next_agent_id = condition["next_agent_id"]
                agent.add_condition(condition_func, next_agent_id)

        # Initialize the state machine with the starting agent and the general prompt
        state_machine = StateMachine(agents["initial_agent"], agents, general_system_prompt)
        return state_machine
