import os
import sys
import importlib.util
import types

# Path to your local scikit-fuzzy directory
scikit_fuzzy_path = os.path.join(os.path.dirname(__file__), "scikit-fuzzy")

# Create a module object
skfuzzy = types.ModuleType("skfuzzy")

# Add to sys.modules
sys.modules["skfuzzy"] = skfuzzy

# Walk through all Python files in scikit-fuzzy directory
for root, dirs, files in os.walk(scikit_fuzzy_path):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            module_name = (
                "skfuzzy"
                + full_path.replace(scikit_fuzzy_path, "").replace("/", ".").replace(".py", "")
            )
            if module_name.endswith("__init__"):
                module_name = module_name.rsplit(".", 1)[0]

            spec = importlib.util.spec_from_file_location(module_name, full_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            try:
                spec.loader.exec_module(mod)
            except Exception as e:
                print(f"Failed to load {module_name}: {e}")


# Import modules from the now-loaded skfuzzy
from skfuzzy import control as ctrl
import skfuzzy as fuzz

# === Your original fuzzy system code === #
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
