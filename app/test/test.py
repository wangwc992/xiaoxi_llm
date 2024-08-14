max_explain_score = 0.9
distance = 0.8 if max_explain_score > 0.8 else 0.5 if max_explain_score > 0.5 else 0
print(distance)