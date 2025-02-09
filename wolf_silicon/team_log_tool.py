from wolf_silicon_env import WolfSiliconEnv

def write_my_log(role:str, message:str) -> str:
    """Write a log message in the team log."""
    WolfSiliconEnv().update_log(role, message)
    return "Log updated."

def view_team_log() -> str:
    """Check the team log to review the latest updates from the team."""
    return WolfSiliconEnv().read_log()