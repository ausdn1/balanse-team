import itertools

def balance_teams(player_list):
    if len(player_list) < 10:
        return None, None, 0
    combinations = list(itertools.combinations(player_list, 5))
    total_score = sum(p['score'] for p in player_list)
    best_diff = float('inf')
    best_teams = (None, None)
    for team_a in combinations:
        score_a = sum(p['score'] for p in team_a)
        score_b = total_score - score_a
        diff = abs(score_a - score_b)
        if diff < best_diff:
            best_diff = diff
            best_teams = (team_a, [p for p in player_list if p not in team_a])
    return best_teams[0], best_teams[1], best_diff