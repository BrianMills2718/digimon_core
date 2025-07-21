import pytest
import random
import numpy as np
import os

@pytest.fixture(autouse=True)
def seed_everything():
    """
    Fixture to seed all relevant random number generators for test determinism.
    This runs automatically for every test function.
    """
    seed_value = 42
    random.seed(seed_value)
    np.random.seed(seed_value)
    os.environ['PYTHONHASHSEED'] = str(seed_value)
    # Add other library-specific seeds here if needed, e.g.:
    # torch.manual_seed(seed_value) 