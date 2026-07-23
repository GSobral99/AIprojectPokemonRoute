import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

'''
Cria um sistema Fuzzy que recebe como input a diferença dos niveis
e o efeito do ataque e devolve como input a probabilidade de ganhar
'''
level_diff = ctrl.Antecedent(np.arange(-9, 10, 1), 'level_diff')
effect = ctrl.Antecedent(np.arange(0, 4.1, 0.1), 'effect')
probabilidade = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'probabilidade')

level_diff['low'] = fuzz.trapmf(level_diff.universe, [-9, -9, -3,-1])
level_diff['medium'] = fuzz.trimf(level_diff.universe, [-1, 0, 1])
level_diff['high'] = fuzz.trapmf(level_diff.universe, [1, 3, 9, 9])

effect['immune'] = fuzz.trapmf(effect.universe, [0, 0, 0, 0.1])
effect['weak'] = fuzz.trimf(effect.universe, [0.1, 0.5, 0.7])
effect['neutral'] = fuzz.trimf(effect.universe, [0.7, 1.0, 1.4])
effect['strong'] = fuzz.trapmf(effect.universe, [1.4, 2.0, 4.0, 4.0])

probabilidade['low'] = fuzz.trimf(probabilidade.universe, [0.0, 0.0, 0.5])
probabilidade['medium'] = fuzz.trimf(probabilidade.universe, [0.0, 0.5, 1.0])
probabilidade['high'] = fuzz.trimf(probabilidade.universe, [0.5, 1.0, 1.0])

# 1. IMMUNE
rule1 = ctrl.Rule(effect['immune'] & level_diff['low'], probabilidade['low'])
rule2 = ctrl.Rule(effect['immune'] & level_diff['medium'], probabilidade['low'])
rule3 = ctrl.Rule(effect['immune'] & level_diff['high'], probabilidade['low'])

# 2. WEAK
rule4 = ctrl.Rule(effect['weak'] & level_diff['low'], probabilidade['low'])
rule5 = ctrl.Rule(effect['weak'] & level_diff['medium'], probabilidade['low'])
rule6 = ctrl.Rule(effect['weak'] & level_diff['high'], probabilidade['medium'])

# 3. NEUTRAL
rule7 = ctrl.Rule(effect['neutral'] & level_diff['low'], probabilidade['low'])
rule8 = ctrl.Rule(effect['neutral'] & level_diff['medium'], probabilidade['medium'])
rule9 = ctrl.Rule(effect['neutral'] & level_diff['high'], probabilidade['high'])

# 4. STRONG
rule10 = ctrl.Rule(effect['strong'] & level_diff['low'], probabilidade['medium'])
rule11 = ctrl.Rule(effect['strong'] & level_diff['medium'], probabilidade['high'])
rule12 = ctrl.Rule(effect['strong'] & level_diff['high'], probabilidade['high'])

rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12]



def calculate_prob(level_input, effect_input):
    #p1
    lvl_pos = np.where(level_diff.universe == level_input)[0][0]
    eff_pos = np.where(effect.universe == effect_input)[0][0]

    #p2
    lvls_diffs = {
        label: level_diff[label].mf[lvl_pos]
        for label in [ 'low', 'medium', 'high']
    }

    effects = {
        label: effect[label].mf[eff_pos]
        for label in ['immune', 'weak', 'neutral', 'strong']
    }

    #p3 e p4
    aggregated = np.zeros_like(probabilidade.universe)
    for rule in rules:
        conditions = rule.antecedent_terms
        conclusion = rule.consequent[0].term

        membership = []
        for term in conditions:
            var_label  = term.parent.label
            term_label = term.label
            if var_label == 'level_diff':
                membership.append(lvls_diffs[term_label])
            else:
                membership.append(effects[term_label])
        rule_strength = min(membership) if membership else 0.0

        if rule_strength > 0:
            contribution = np.fmin(rule_strength, conclusion.mf)
            aggregated = np.fmax(aggregated, contribution)

    #5
    if np.sum(aggregated) == 0:
        return 0.5

    result = fuzz.defuzz(probabilidade.universe, aggregated, 'centroid')
    return float(np.clip(result, 0.0, 1.0))