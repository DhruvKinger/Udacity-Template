# UdaciHealth – Diabetes Risk Pre-Screening (PyTorch MLP)

Neural-network pre-screening model trained on the CDC Diabetes Health Indicators data (BRFSS 2015).
All work is in **`diabetes_prediction_mlp.ipynb`** (all cells executed, outputs included).

## Results (test set, threshold 0.5)
| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Baseline MLP (128-64) – Section 5 | 0.746 | 0.723 | 0.798 | 0.758 | 0.824 |
| Final: + dropout 0.5 | 0.752 | 0.721 | 0.821 | 0.768 | 0.831 |

* Dropout 0.5 gives +6.7 % relative recall vs. the in-table baseline (single seed); over 3 seeds the mean gain is +2.5 % recall, +1.1 % F1, +0.8 % AUC, with 3–4x lower variance. See Section 6.4/6.5 for the caveats.
* Realistic ceiling for these self-reported survey features is ~75 % accuracy / 0.83 AUC (not 95–99 %).
* Stand-out work: weight decay, early stopping, LR scheduler, batch size, feature engineering, and the original imbalanced dataset with `pos_weight`.

## Structure
```
diabetes_prediction_mlp.ipynb   main notebook
data/                           balanced + original CSVs, data_dictionary.md
results/experiment_results.csv  comparison table (Section 6.4)
models/diabetes_mlp_final.pt    final weights, config, scaler statistics
requirements.txt
```

## Run
```
pip install -r requirements.txt
jupyter notebook diabetes_prediction_mlp.ipynb
```
Runtime is about 20 minutes on a single CPU core; seeds are fixed, but exact numbers can vary slightly across hardware / PyTorch versions.
