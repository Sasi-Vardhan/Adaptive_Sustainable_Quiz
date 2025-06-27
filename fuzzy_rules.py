import os
import sys
import types
import importlib.util
import numpy as np

# Path to the skfuzzy source inside your project
skfuzzy_path = os.path.join(os.path.dirname(__file__), "scikit-fuzzy", "skfuzzy")

# Register base module
skfuzzy_module = types.ModuleType("skfuzzy")
sys.modules["skfuzzy"] = skfuzzy_module

# Recursively load modules (excluding tests)
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
            except Exception as e:
                print(f"⚠️ Failed to load {mod_name}: {e}")

# Import required classes
try:
    from skfuzzy import control as ctrl
    assert hasattr(ctrl, "Antecedent")
except (ImportError, AssertionError):
    # Patch manually if __init__.py doesn't expose classes
    from skfuzzy.control import variable, controlsystem, rule, term
    ctrl = types.SimpleNamespace(
        Antecedent=variable.Antecedent,
        Consequent=variable.Consequent,
        ControlSystem=controlsystem.ControlSystem,
        ControlSystemSimulation=controlsystem.ControlSystemSimulation,
        Rule=rule.Rule,
        Term=term.Term
    )

import skfuzzy as fuzz

# === Fuzzy Logic System ===
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

    for antecedent in [p_e, p_m, p_h]:
        antecedent['low'] = fuzz.trimf(antecedent.universe, [0, 0, 0.5])
        antecedent['medium'] = fuzz.trimf(antecedent.universe, [0.3, 0.5, 0.8])
        antecedent['high'] = fuzz.trimf(antecedent.universe, [0.5, 0.75, 1])

    easy_streak['low'] = fuzz.trimf(easy_streak.universe, [0, 0, 2])
    easy_streak['medium'] = fuzz.trimf(easy_streak.universe, [1, 2, 4])
    easy_streak['high'] = fuzz.trimf(easy_streak.universe, [3, 5, 15])

    medium_streak['low'] = fuzz.trimf(medium_streak.universe, [0, 0, 2])
    medium_streak['medium'] = fuzz.trimf(medium_streak.universe, [1, 2, 4])
    medium_streak['high'] = fuzz.trimf(medium_streak.universe, [3, 5, 15])

    difficulty['easy'] = fuzz.trimf(difficulty.universe, [0, 0, 0.7])
    difficulty['medium'] = fuzz.trimf(difficulty.universe, [0.3, 1, 1.7])
    difficulty['hard'] = fuzz.trimf(difficulty.universe, [1.3, 2, 2])

    rules = [
        ctrl.Rule(total_correct['high'] & success_rate['high'] & p_h['high'], difficulty['hard']),
        ctrl.Rule(total_correct['high'] & success_rate['medium'] & p_m['high'], difficulty['medium']),
        ctrl.Rule(easy_streak['high'] & p_m['medium'], difficulty['medium']),
        ctrl.Rule(medium_streak['high'] & p_h['medium'], difficulty['hard']),
        ctrl.Rule(total_correct['medium'] & success_rate['medium'], difficulty['medium']),
        ctrl.Rule(total_correct['medium'] & success_rate['low'] & p_m['medium'], difficulty['medium']),
        ctrl.Rule(total_correct['medium'] & success_rate['low'] & p_e['high'], difficulty['easy']),
        ctrl.Rule(total_correct['low'] & success_rate['low'], difficulty['easy']),
        ctrl.Rule(total_correct['low'] & success_rate['medium'] & p_m['medium'], difficulty['medium']),
        ctrl.Rule(p_e['low'] & p_m['low'] & p_h['low'], difficulty['easy']),
        ctrl.Rule(p_e['high'] & p_m['high'] & p_h['high'], difficulty['hard']),
        ctrl.Rule(total_correct['medium'] & success_rate['high'], difficulty['hard']),
        ctrl.Rule(total_correct['low'] & success_rate['high'] & p_m['medium'], difficulty['medium']),
        ctrl.Rule(easy_streak['medium'] & p_m['medium'], difficulty['medium']),
        ctrl.Rule(medium_streak['medium'] & p_h['medium'], difficulty['hard']),
    ]

    difficulty_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(difficulty_ctrl)
