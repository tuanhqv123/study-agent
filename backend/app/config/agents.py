"""
Configuration for different AI agents/models available in the application.
Each agent is configured with a unique ID, model name, and display name (trùng với model).
"""

AVAILABLE_AGENTS = {
    "qwen3-1.7b": {
        "id": "qwen3-1.7b",
        "model": "qwen3-1.7b",
        "display_name": "qwen3-1.7b",
        "temperature": 0.7,
        "is_default": False
    },
    "qwen3-4b": {
        "id": "qwen3-4b",
        "model": "qwen3-4b",
        "display_name": "qwen3-4b",
        "temperature": 0.7,
        "is_default": True
    },
    "qwen3-8b": {
        "id": "qwen3-8b",
        "model": "qwen3-8b",
        "display_name": "qwen3-8b",
        "temperature": 0.7,
        "is_default": False
    },
    "gemma-3-1b-it": {
        "id": "gemma-3-1b-it",
        "model": "gemma-3-1b-it",
        "display_name": "gemma-3-1b-it",
        "temperature": 0.7,
        "is_default": False
    }
}

# Helper function to get agent by ID
def get_agent(agent_id):
    """
    Retrieves agent configuration by ID.
    Falls back to default agent if requested ID doesn't exist.
    
    Args:
        agent_id (str): The ID of the agent to retrieve
        
    Returns:
        dict: Agent configuration dictionary
    """
    if agent_id in AVAILABLE_AGENTS:
        return AVAILABLE_AGENTS[agent_id]
    
    # Return default agent if requested agent isn't found
    for agent in AVAILABLE_AGENTS.values():
        if agent.get("is_default", False):
            return agent
    
    # Fallback to first agent if no default is set
    return list(AVAILABLE_AGENTS.values())[0]

# Helper function to get all available agents
def get_all_agents():
    """
    Returns a list of all available agents.
    
    Returns:
        list: List of agent configuration dictionaries
    """
    return list(AVAILABLE_AGENTS.values()) 