import pytest 
from env_v2.env import Env2


class TestEnv2:
    
    def setup_method(self):
        print("setup")
        
    def test_a(self):
        self.assertEqual(1, 1)