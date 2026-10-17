# Data Dictionary – CDC Diabetes Health Indicators (BRFSS 2015)

Source: CDC Behavioral Risk Factor Surveillance System (BRFSS) 2015 telephone health survey, as published on Kaggle
(`alexteboul/diabetes-health-indicators-dataset`).

| File | Rows | Description |
|---|---|---|
| `diabetes_data.csv` | 70,692 | **Balanced 50/50** subset (35,346 per class). Used for Sections 1–6. |
| `diabetes_binary_health_indicators_BRFSS2015.csv` | 253,680 | Original, imbalanced data (~13.9 % diabetes). Used in the stand-out experiment (6.6.2). |

## Target
| Column | Meaning |
|---|---|
| `Diabetes_binary` | 0 = no diabetes, 1 = prediabetes or diabetes |

## Features (21)
| Column | Type | Values / meaning |
|---|---|---|
| `HighBP` | binary | 1 = told by a professional that blood pressure is high |
| `HighChol` | binary | 1 = told that cholesterol is high |
| `CholCheck` | binary | 1 = cholesterol checked in the past 5 years |
| `BMI` | numeric | Body-mass index (kg/m²) |
| `Smoker` | binary | 1 = has smoked at least 100 cigarettes in lifetime |
| `Stroke` | binary | 1 = ever told had a stroke |
| `HeartDiseaseorAttack` | binary | 1 = coronary heart disease or myocardial infarction |
| `PhysActivity` | binary | 1 = physical activity in the past 30 days (outside of work) |
| `Fruits` | binary | 1 = eats fruit at least once per day |
| `Veggies` | binary | 1 = eats vegetables at least once per day |
| `HvyAlcoholConsump` | binary | 1 = heavy drinker (men >14, women >7 drinks/week) |
| `AnyHealthcare` | binary | 1 = has any kind of health-care coverage |
| `NoDocbcCost` | binary | 1 = could not see a doctor in the past year because of cost |
| `GenHlth` | ordinal 1–5 | Self-rated general health: 1 = excellent … 5 = poor |
| `MentHlth` | numeric 0–30 | Days of poor mental health in the past 30 days |
| `PhysHlth` | numeric 0–30 | Days of poor physical health in the past 30 days |
| `DiffWalk` | binary | 1 = serious difficulty walking or climbing stairs |
| `Sex` | binary | 0 = female, 1 = male |
| `Age` | ordinal 1–13 | 5-year age bands: 1 = 18–24, 2 = 25–29, … 9 = 60–64, … 13 = 80 or older |
| `Education` | ordinal 1–6 | 1 = never attended school / kindergarten only … 6 = college graduate |
| `Income` | ordinal 1–8 | 1 = less than $10,000 … 8 = $75,000 or more |

## Clinical notes
* Most features are self-reported survey answers; there are **no laboratory values** (glucose, HbA1c), which limits the achievable accuracy.
* Label 1 combines diabetes and prediabetes.
* In screening, a **false negative** (a missed diabetic) delays diagnosis and treatment and is usually more costly than a **false positive** (an extra confirmatory test).
