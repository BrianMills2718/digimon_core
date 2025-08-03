#!/usr/bin/env python3
"""
Example: Run logistic regression on KGAS ProcessingResult output
- Loads a ProcessingResult (JSON or Python object)
- Converts entities/relationships to pandas DataFrame
- Runs logistic regression using statsmodels.Logit
"""
import json
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

# Load ProcessingResult from JSON file (replace with your file path)
with open('processing_result.json') as f:
    result = json.load(f)

# Example: Assume relationships have 'confidence' and a binary label 'is_true'
rels = result['relationships']
df = pd.DataFrame(rels)

# Example: Use 'confidence' as predictor, 'is_true' as target
X = df[['confidence']]
y = df['is_true']
X = sm.add_constant(X)

# Fit logistic regression
model = sm.Logit(y, X)
fit = model.fit()

print(fit.summary())

# Predict probabilities
probs = fit.predict(X)
df['predicted_prob'] = probs
print(df[['confidence', 'is_true', 'predicted_prob']].head())

# Save results
out_path = Path('logit_results.csv')
df.to_csv(out_path, index=False)
print(f"Results saved to {out_path}") 