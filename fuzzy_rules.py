import os
import sys
import types
import importlib.util
import numpy as np

# Path to the skfuzzy source inside the project
skfuzzy_path = os.path.join(os.path.dirname(__file__), "scikit-fuzzy", "skfuzzy")

# Create the base module
skfuzzy_module = types.ModuleType("skfuzzy")
sys.modules["skfuzzy"] = skfuzzy_module

# Recursively load modules EXCEPT tests
loaded_modules = []
for root, dirs, files in os.walk(skfuzzy_path):
    if "test" in root or "tests" in root:
        continue

    for file in files:
        if file.endswith(".py") and not file.startswith("test"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, skfuzzy_path)
            mod_name = "skfuzzy." + rel_path.replace(os.sep, ".").replace(".py", "")
            if mod_name.endswith(".__init__"):
                mod_name = mod_name.rsplit(".", 1)[0]

            try:
                spec = importlib.util.spec_from_file_location(mod_name, full_path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)
                loaded_modules.append(mod_name)
            except Exception as e:
                print(f"⚠️ Failed to load {mod_name}: {e}")

# DEBUG: ensure control module is imported
if "skfuzzy.control" not in sys.modules:
    print("❌ skfuzzy.control not loaded!")

# Now import fuzzy modules
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# === Your fuzzy logic system === #
def setup_fuzzy_system():
    total_correct = ctrl.Antecedent(np.arange(0, 16, 1), 'total_correct')
    success_rate = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'success_rate')
    p_e = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_e')
    p_m = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_m')
    p_h = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_h')
    easy_streak = ctrl.Antecedent(np.arange(0, 16, 1), 'easy_streak')
    medium_streak = ctrl.Antecedent(np.arange(0, 16, 1), 'medium_streak')

    difficulty = ctrl.Consequent(np.arange(0, 2.01, 0.01), 'difficulty')

    total_correct['low'] = fuzz.trimf(total_correct.universe, [0, 0, 6])
    total_correct['medium'] = fuzz.trimf(total_correct.universe, [3, 7, 11])
    total_correct['high'] = fuzz.trimf(total_correct.universe, [8, 12, 15])

    success_rate['low'] = fuzz.trimf(success_rate.universe, [0, 0, 0.5])
    success_rate['medium'] = fuzz.trimf(success_rate.universe, [0.3, 0.5, 0.8])
    success_rate['high'] = fuzz.trimf(success_rate.universe, [0.5, 0.75, 1])

    p_e['low'] = fuzz.trimf(p_e.universe, [0, 0, 0.5])
    p_e['medium'] = fuzz.trimf(p_e.universe, [0.3, 0.5, 0.8])
    p_e['high'] = fuzz.trimf(p_e.universe, [0.5, 0.75, 1])

    p_m['low'] = fuzz.trimf(p_m.universe, [0, 0, 0.5])
    p_m['medium'] = fuzz.trimf(p_m.universe, [0.3, 0.5, 0.8])
    p_m['high'] = fuzz.trimf(p_m.universe, [0.5, 0.75, 1])

    p_h['low'] = fuzz.trimf(p_h.universe, [0, 0, 0.5])
    p_h['medium'] = fuzz.trimf(p_h.universe, [0.3, 0.5, 0.8])
    p_h['high'] = fuzz.trimf(p_h.universe, [0.5, 0.75, 1])

    easy_streak['low'] = fuzz.trimf(easy_streak.universe, [0, 0, 2])
    easy_streak['medium'] = fuzz.trimf(easy_streak.universe, [1, 2, 4])
    easy_streak['high'] = fuzz.trimf(easy_streak.universe, [3, 5, 15])

    medium_streak['low'] = fuzz.trimf(medium_streak.universe, [0, 0, 2])
    medium_streak['medium'] = fuzz.trimf(medium_streak.universe, [1, 2, 4])
    medium_streak['high'] = fuzz.trimf(medium_streak.universe, [3, 5, 15])

    difficulty['easy'] = fuzz.trimf(difficulty.universe, [0, 0, 0.7])
    difficulty['medium'] = fuzz.trimf(difficulty.universe, [0.3, 1, 1.7])
    difficulty['hard'] = fuzz.trimf(difficulty.universe, [1.3, 2, 2])

    rule1 = ctrl.Rule(total_correct['high'] & success_rate['high'] & p_h['high'], difficulty['hard'])
    rule2 = ctrl.Rule(total_correct['high'] & success_rate['medium'] & p_m['high'], difficulty['medium'])
    rule3 = ctrl.Rule(easy_streak['high'] & p_m['medium'], difficulty['medium'])
    rule4 = ctrl.Rule(medium_streak['high'] & p_h['medium'], difficulty['hard'])
    rule5 = ctrl.Rule(total_correct['medium'] & success_rate['medium'], difficulty['medium'])
    rule6 = ctrl.Rule(total_correct['medium'] & success_rate['low'] & p_m['medium'], difficulty['medium'])
    rule7 = ctrl.Rule(total_correct['medium'] & success_rate['low'] & p_e['high'], difficulty['easy'])
    rule8 = ctrl.Rule(total_correct['low'] & success_rate['low'], difficulty['easy'])
    rule9 = ctrl.Rule(total_correct['low'] & success_rate['medium'] & p_m['medium'], difficulty['medium'])
    rule10 = ctrl.Rule(p_e['low'] & p_m['low'] & p_h['low'], difficulty['easy'])
    rule11 = ctrl.Rule(p_e['high'] & p_m['high'] & p_h['high'], difficulty['hard'])
    rule12 = ctrl.Rule(total_correct['medium'] & success_rate['high'], difficulty['hard'])
    rule13 = ctrl.Rule(total_correct['low'] & success_rate['high'] & p_m['medium'], difficulty['medium'])
    rule14 = ctrl.Rule(easy_streak['medium'] & p_m['medium'], difficulty['medium'])
    rule15 = ctrl.Rule(medium_streak['medium'] & p_h['medium'], difficulty['hard'])

    difficulty_ctrl = ctrl.ControlSystem([
        rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
        rule11, rule12, rule13, rule14, rule15
    ])
    return ctrl.ControlSystemSimulation(difficulty_ctrl)
