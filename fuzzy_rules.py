import numpy as np
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the module manually and alias it as 'skfuzzy'
import scikit_fuzzy as skfuzzy  # <
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def setup_fuzzy_system():
    # Define input variables
    total_correct = ctrl.Antecedent(np.arange(0, 16, 1), 'total_correct')
    success_rate = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'success_rate')
    p_e = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_e')
    p_m = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_m')
    p_h = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_h')
    easy_streak = ctrl.Antecedent(np.arange(0, 16, 1), 'easy_streak')
    medium_streak = ctrl.Antecedent(np.arange(0, 16, 1), 'medium_streak')

    # Define output variable
    difficulty = ctrl.Consequent(np.arange(0, 2.01, 0.01), 'difficulty')

    # Define membership functions with more overlap
    total_correct['low'] = fuzz.trimf(total_correct.universe, [0, 0, 6])  # Adjusted for more overlap
    total_correct['medium'] = fuzz.trimf(total_correct.universe, [3, 7, 11])
    total_correct['high'] = fuzz.trimf(total_correct.universe, [8, 12, 15])

    success_rate['low'] = fuzz.trimf(success_rate.universe, [0, 0, 0.5])  # Adjusted for more overlap
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

    easy_streak['low'] = fuzz.trimf(easy_streak.universe, [0, 0, 2])  # Adjusted for more overlap
    easy_streak['medium'] = fuzz.trimf(easy_streak.universe, [1, 2, 4])
    easy_streak['high'] = fuzz.trimf(easy_streak.universe, [3, 5, 15])

    medium_streak['low'] = fuzz.trimf(medium_streak.universe, [0, 0, 2])
    medium_streak['medium'] = fuzz.trimf(medium_streak.universe, [1, 2, 4])
    medium_streak['high'] = fuzz.trimf(medium_streak.universe, [3, 5, 15])

    difficulty['easy'] = fuzz.trimf(difficulty.universe, [0, 0, 0.7])
    difficulty['medium'] = fuzz.trimf(difficulty.universe, [0.3, 1, 1.7])
    difficulty['hard'] = fuzz.trimf(difficulty.universe, [1.3, 2, 2])

    # Define more comprehensive fuzzy rules
    rule1 = ctrl.Rule(total_correct['high'] & success_rate['high'] & p_h['high'], difficulty['hard'])
    rule2 = ctrl.Rule(total_correct['high'] & success_rate['medium'] & p_m['high'], difficulty['medium'])
    rule3 = ctrl.Rule(easy_streak['high'] & p_m['medium'], difficulty['medium'])  # Relaxed p_m requirement
    rule4 = ctrl.Rule(medium_streak['high'] & p_h['medium'], difficulty['hard'])  # Relaxed p_h requirement
    rule5 = ctrl.Rule(total_correct['medium'] & success_rate['medium'], difficulty['medium'])
    rule6 = ctrl.Rule(total_correct['medium'] & success_rate['low'] & p_m['medium'], difficulty['medium'])
    rule7 = ctrl.Rule(total_correct['medium'] & success_rate['low'] & p_e['high'], difficulty['easy'])
    rule8 = ctrl.Rule(total_correct['low'] & success_rate['low'], difficulty['easy'])  # Adjusted to require both
    rule9 = ctrl.Rule(total_correct['low'] & success_rate['medium'] & p_m['medium'], difficulty['medium'])
    rule10 = ctrl.Rule(p_e['low'] & p_m['low'] & p_h['low'], difficulty['easy'])
    rule11 = ctrl.Rule(p_e['high'] & p_m['high'] & p_h['high'], difficulty['hard'])

    # Additional rules to cover more scenarios
    rule12 = ctrl.Rule(total_correct['medium'] & success_rate['high'], difficulty['hard'])
    rule13 = ctrl.Rule(total_correct['low'] & success_rate['high'] & p_m['medium'], difficulty['medium'])
    rule14 = ctrl.Rule(easy_streak['medium'] & p_m['medium'], difficulty['medium'])
    rule15 = ctrl.Rule(medium_streak['medium'] & p_h['medium'], difficulty['hard'])

    # Create control system
    difficulty_ctrl = ctrl.ControlSystem([
        rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
        rule11, rule12, rule13, rule14, rule15
    ])
    return ctrl.ControlSystemSimulation(difficulty_ctrl)
