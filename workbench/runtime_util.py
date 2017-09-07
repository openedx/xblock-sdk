"""
Runtime utilities
"""

from .runtime import WORKBENCH_KVS, ID_MANAGER
from .scenarios import init_scenarios


def reset_global_state():
    """
    Reset any global state in the workbench.

    This allows us to write properly isolated tests.

    """
    WORKBENCH_KVS.clear()
    ID_MANAGER.clear()
    init_scenarios()
