agent_runs = {}


def save_run(run_id: str, run_data: dict):
    agent_runs[run_id] = run_data


def get_run(run_id: str):
    return agent_runs.get(run_id)