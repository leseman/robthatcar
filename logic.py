import math
import config

def update_floating_scores(game_state):
    for score in game_state.floating_scores[:]:
        score['time'] -= 1
        score['pos'].y -= 1  # Move the score up
        if score['time'] <= 0:
            game_state.floating_scores.remove(score)

def calculate_score(distance, game_state):
    max_distance = math.sqrt(config.WIDTH**2 + config.HEIGHT**2)
    
    # Calculate multiplier based on distance
    multiplier = 1 + (distance / max_distance) * (game_state.max_multiplier - 1)
    
    # Calculate final score
    score = int(game_state.base_score * multiplier)
    
    return score