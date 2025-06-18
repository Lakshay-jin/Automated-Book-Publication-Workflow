import numpy as np
import random
from collections import defaultdict

class RLSearchAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = defaultdict(lambda: defaultdict(float))  # Q[state][action]
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # exploration

    def choose_action(self, state, actions):
        if not actions:
            return None  # 🛑 Safeguard for empty input

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(actions)

        q_vals = {a: self.q_table[state][a] for a in actions}
        
        if not q_vals:
            return random.choice(actions)  # fallback if no Q-values exist

        return max(q_vals, key=q_vals.get)

    def update(self, state, action, reward, next_state, next_actions):
        max_future = max([self.q_table[next_state][a] for a in next_actions], default=0)
        current = self.q_table[state][action]
        self.q_table[state][action] += self.alpha * (reward + self.gamma * max_future - current)
