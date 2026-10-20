# Patient Selection for Diabetes Drug Testing
## Learner Feedback Templates

Use the feedback under the matching result for each rubric point.

---

# Exploratory Data Analysis

## Rubric Point: Visual Analysis of Missing Values and Cardinality

**Requirement:** Uses visualizations to identify fields with high amounts of missing or null values and fields with high cardinality. Correctly identifies fields with many missing or zero values, fields with approximately Gaussian distributions based on histograms, and describes age and gender distributions. Justifies why fields have high cardinality. TensorFlow Data Validation visualizations are optional.

### Pass

## Excellent work!

Your exploratory analysis uses visualizations to identify missing or zero values, distribution shapes, and high-cardinality fields. The explanations make clear why particular fields need attention, and the age and gender distributions are described appropriately.

Continue using the findings to guide data-quality decisions and feature selection.

**Further reading:** [TensorFlow Data Validation](https://www.tensorflow.org/tfx/data_validation/get_started)

### Fail

## Keep refining your analysis

The exploratory analysis does not yet identify or explain all required data patterns. Check missing and zero values, use histograms to assess distribution shapes, identify high-cardinality fields, and explain why their cardinality is high. Include clear descriptions of age and gender distributions. TensorFlow Data Validation visualizations are optional.

**Further reading:** [TensorFlow Data Validation](https://www.tensorflow.org/tfx/data_validation/get_started)

---

## Rubric Point: Feature Selection from Exploratory Analysis

**Requirement:** Selects features based on exploratory analysis and uses supporting analysis to justify whether `payer_code` and `weight` should be included or excluded.

### Pass

## Good analytical reasoning

Your feature-selection decisions are supported by exploratory findings. The explanation addresses `payer_code` and `weight` and connects the decision to evidence from the dataset rather than relying on assumptions alone.

Continue documenting how data quality and feature characteristics influence the final selection.

**Further reading:** [TensorFlow Data Analysis](https://www.tensorflow.org/tfx/data_analysis/get_started)

### Fail

## Support feature choices with evidence

The feature-selection decisions are not yet sufficiently justified. Review `payer_code` and `weight`, examine the relevant data patterns, and explain why each field should be included or excluded based on the findings.

**Further reading:** [TensorFlow Data Analysis](https://www.tensorflow.org/tfx/data_analysis/get_started)

---

# Data Preparation

## Rubric Point: EHR Data Level and Transformations

**Requirement:** Uses the appropriate line, encounter, or patient level for the EHR dataset and applies suitable transformations, aggregations, and filters.

### Pass

## Well-structured data preparation

Your data preparation uses an appropriate level for the task and applies transformations, aggregations, and filters consistently. Choosing the correct unit of analysis helps ensure that the prepared data represents the intended prediction task.

Continue checking that each transformation preserves the meaning and relationships of the EHR records.

**Further reading:** [TensorFlow Data Analysis](https://www.tensorflow.org/tfx/data_analysis/get_started)

### Fail

## Check the level of analysis

The data preparation does not yet demonstrate the appropriate EHR data level or transformations. Review whether the task operates at the line, encounter, or patient level, then verify the related aggregation, filtering, and transformation steps.

**Further reading:** [TensorFlow Data Analysis](https://www.tensorflow.org/tfx/data_analysis/get_started)

---

## Rubric Point: Dimensionality Reduction for High-Cardinality Codes

**Requirement:** Correctly reduces dimensionality for a dataset field containing a high-cardinality code set.

### Pass

## Effective dimensionality reduction

Your approach reduces the complexity of a high-cardinality code field while keeping the representation useful for analysis. This helps make the dataset more manageable for downstream modeling.

Continue checking that the grouping or mapping approach preserves meaningful distinctions in the data.

**Further reading:** [TensorFlow feature columns](https://www.tensorflow.org/guide/feature_columns)

### Fail

## Simplify high-cardinality fields

The dimensionality-reduction step does not yet meet the requirement. Review the high-cardinality code field and apply a suitable reduction or grouping strategy. Check that the resulting representation remains meaningful for the modeling task.

**Further reading:** [TensorFlow feature columns](https://www.tensorflow.org/guide/feature_columns)

---

## Rubric Point: NDC Code Mapping to Generic Drug Names

**Requirement:** Correctly maps NDC codes to generic drug names and prints the correct mappings in the notebook.

### Pass

## Accurate code mapping

Your submission maps NDC codes to generic drug names and displays the mappings for review. Clear mapping output makes it easier to verify that medication codes have been interpreted as intended.

Continue checking the mapping results against the source data and handling codes that cannot be mapped.

**Further reading:** [FDA National Drug Code Directory](https://www.fda.gov/drugs/drug-approvals-and-databases/national-drug-code-directory)

### Fail

## Verify the medication mappings

The NDC mapping does not yet meet all requirements. Check that codes are mapped to the correct generic drug names and that the resulting mappings are printed in the notebook. Review missing or unmatched codes rather than silently treating them as valid mappings.

**Further reading:** [FDA National Drug Code Directory](https://www.fda.gov/drugs/drug-approvals-and-databases/national-drug-code-directory)

---

## Rubric Point: Train, Validation, and Test Splits Without Leakage

**Requirement:** Splits the original dataset into train, validation, and test datasets correctly, avoids patient or encounter leakage, and passes the Encounter Test.

### Pass

## Careful dataset splitting

Your submission creates the required train, validation, and test datasets and addresses patient or encounter leakage. This is important for evaluating how well the model generalizes beyond records it has already seen.

Continue checking the split logic and rerunning the Encounter Test whenever the data-preparation process changes.

**Further reading:** [Scikit-learn — Data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)

### Fail

## Prevent data leakage

The dataset split does not yet meet all requirements. Verify that train, validation, and test sets are created correctly and that records from the same patient or encounter do not leak across splits. Run the Encounter Test and resolve any failures before evaluating the model.

**Further reading:** [Scikit-learn — Data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)

---

# Feature Engineering

## Rubric Point: Categorical Feature Transformation

**Requirement:** Completes the categorical feature transformer using TensorFlow's feature column API and successfully transforms the demo dataset with at least one new categorical feature.

### Pass

## Good categorical feature engineering

Your categorical transformer follows the required feature-column workflow and successfully applies it to the demo dataset. Demonstrating a new categorical feature helps show that the transformation works in practice.

Continue checking that categorical values are handled consistently, including unexpected or missing values.

**Further reading:** [TensorFlow feature columns](https://www.tensorflow.org/guide/feature_columns)

### Fail

## Complete the categorical transformer

The categorical feature transformer does not yet meet all requirements. Complete the provided function using TensorFlow's feature column API and demonstrate it on the demo dataset with at least one new categorical feature.

**Further reading:** [TensorFlow feature columns](https://www.tensorflow.org/guide/feature_columns)

---

## Rubric Point: Numerical Feature Transformation and Normalization

**Requirement:** Completes the numerical feature transformer using TensorFlow's feature column API, demonstrates at least one new numerical feature on the demo dataset, and correctly uses the provided z-score normalizer or another custom normalizer.

### Pass

## Consistent numerical transformation

Your numerical transformer applies the required feature-column workflow and demonstrates a new numerical feature on the demo dataset. The normalization step supports consistent numerical inputs for modeling.

Continue verifying that normalization is applied correctly and that the transformation behaves as expected on different values.

**Further reading:** [TensorFlow feature columns](https://www.tensorflow.org/guide/feature_columns)

### Fail

## Complete the numerical transformer

The numerical feature transformer does not yet meet all requirements. Complete the function, demonstrate at least one new numerical feature on the demo dataset, and correctly incorporate the provided z-score normalizer or another suitable custom normalizer.

**Further reading:** [TensorFlow feature columns](https://www.tensorflow.org/guide/feature_columns)

---

# Model Building and Analysis

## Rubric Point: Regression Predictions, Uncertainty, and Binary Outputs

**Requirement:** Uses TensorFlow Probability to produce mean and standard-deviation predictions and creates a prediction dataset with labels correctly mapped to binary predictions and actual values.

### Pass

## Clear prediction preparation

Your submission prepares regression-model predictions for uncertainty analysis and organizes the binary classification outputs with correctly mapped predicted and actual labels. Reporting mean and standard deviation provides additional information about prediction uncertainty.

Continue checking label mappings and prediction outputs so that the results can be interpreted consistently.

**Further reading:** [TensorFlow Probability](https://www.tensorflow.org/probability)

### Fail

## Verify prediction outputs

The prediction preparation does not yet meet all requirements. Check the TensorFlow Probability outputs for mean and standard deviation, then ensure the prediction dataset maps predicted and actual labels correctly to binary values.

**Further reading:** [TensorFlow Probability](https://www.tensorflow.org/probability)

---

## Rubric Point: Classification Metrics

**Requirement:** Evaluates model predictions using AUC, F1, precision, and recall.

### Pass

## Comprehensive model evaluation

Your submission evaluates the model using the required classification metrics. Considering AUC, F1, precision, and recall gives a broader view of model performance than relying on a single score.

Continue interpreting the metrics together and explaining what they reveal about the model's strengths and limitations.

**Further reading:** [Scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)

### Fail

## Complete the model evaluation

The evaluation does not yet report all required metrics. Calculate AUC, F1, precision, and recall, then explain what the results indicate about the model's performance.

**Further reading:** [Scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)

---

## Rubric Point: Model Summary and Bias–Variance Trade-off

**Requirement:** Completes both model-summary questions and addresses the bias–variance trade-off for the problem.

### Pass

## Thoughtful model analysis

Your submission addresses both model-summary questions and explains the bias–variance trade-off in the context of the problem. This shows consideration of how model complexity may affect performance on unseen data.

Continue connecting the discussion to observed model behavior and evaluation results.

**Further reading:** [Scikit-learn — Underfitting and overfitting](https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html)

### Fail

## Develop the model discussion

The model discussion does not yet address all required points. Complete both model-summary questions and explain the bias–variance trade-off in relation to the problem and the observed model performance.

**Further reading:** [Scikit-learn — Underfitting and overfitting](https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html)

---

## Rubric Point: Aequitas Bias Report for Race and Gender

**Requirement:** Uses Aequitas to create a bias report for race and gender, including visualizations of at least two patient-selection metrics, a reference-group fairness comparison on at least one metric, and justification for at least one visualization.

### Pass

## Important fairness analysis

Your submission uses the Aequitas toolkit to examine patient-selection outcomes across race and gender. The required visualizations and reference-group comparison help make potential disparities visible, while the accompanying justification supports interpretation of the results.

Continue interpreting fairness metrics carefully and explaining what each comparison can and cannot establish.

**Further reading:** [Aequitas documentation](https://aequitas.readthedocs.io/)

### Fail

## Complete the bias analysis

The bias report does not yet meet all requirements. Use Aequitas to analyze race and gender, include visualizations for at least two patient-selection metrics, compare a reference group on at least one fairness metric such as TPR, and justify at least one visualization.

**Further reading:** [Aequitas documentation](https://aequitas.readthedocs.io/)

---

# Overall Project Feedback

Use the feedback matching the final review result.

## Pass

### 🎉 Congratulations on passing!

Congratulations on successfully completing the project! Your work brings together EHR data preparation, feature engineering, model evaluation, and fairness analysis for diabetes drug testing. Keep checking data quality, preventing leakage, interpreting uncertainty, and examining potential bias so your conclusions remain careful and well supported. Every project is a chance to grow — keep it up! 🚀

## Fail

### 💪 Good effort — keep improving!

Thank you for the effort you’ve put into this project. Some requirements still need attention, but you can work through them step by step. Use the rubric feedback to review data quality, dataset splitting, feature transformations, model metrics, and fairness analysis. Test each change and make sure your conclusions are supported by the results. Keep going — each improvement strengthens your work! 🌱

## Ungradable — Required Files Missing

### 📂 Project files required for review

The project cannot be graded because the required files are missing or cannot be opened. Please check the submission requirements and upload the complete files in an accessible format so the work can be reviewed fairly. This is about missing materials, not your ability. Once the files are available, the project can be assessed. 👍
