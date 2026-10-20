import os

import numpy as np
import pandas as pd
import tensorflow as tf

# Number of days a patient must stay in hospital to be a candidate for the trial.
# The drug needs 5-7 days of in-hospital administration, so we use the lower bound.
# (Chosen from the time_in_hospital distribution - see the notebook, Question 2.)
CUTOFF_DAYS = 5

# Categorical fields with more distinct values than this are embedded instead of one-hot encoded
EMBEDDING_VOCAB_THRESHOLD = 50


####### STUDENTS FILL THIS OUT ######
#Question 3
def reduce_dimension_ndc(df, ndc_df):
    '''
    df: pandas dataframe, input dataset
    ndc_df: pandas dataframe, drug code dataset used for mapping in generic names
    return:
        df: pandas dataframe, output dataframe with joined generic drug name
    '''
    # The lookup table repeats a couple of NDC codes (same drug, same name). A plain merge would
    # duplicate the matching dataset lines, so keep exactly one row per NDC code.
    lookup = (ndc_df[['NDC_Code', 'Non-proprietary Name']]
              .drop_duplicates('NDC_Code')
              .rename(columns={'NDC_Code': 'ndc_code',
                               'Non-proprietary Name': 'generic_drug_name'}))
    assert not lookup['ndc_code'].duplicated().any()

    out = df.merge(lookup, on='ndc_code', how='left', validate='many_to_one')

    # Lines with no NDC code mean no drug was recorded for that encounter (this never mixes with
    # real drug lines inside one encounter), so give them an explicit category rather than NaN.
    out['generic_drug_name'] = out['generic_drug_name'].fillna('No_Drug_Recorded')

    # The raw (high cardinality) NDC code is replaced by the generic name. It must be dropped
    # because it varies line to line and would otherwise split one encounter into several groups
    # when the dataset is aggregated to the encounter level later.
    out = out.drop(columns=['ndc_code'])
    return out


def fill_unmeasured_lab_results(df, cols=('max_glu_serum', 'A1Cresult'), fill_value='None'):
    '''
    The data schema says these lab fields are "none" when the test was not measured, but the file
    stores that as a missing value. pandas.groupby silently drops rows whose grouping key is
    NaN, so make the "not measured" level explicit before aggregating.
    '''
    df = df.copy()
    for c in cols:
        df[c] = df[c].fillna(fill_value)
    return df


#Question 4
def select_first_encounter(df):
    '''
    df: pandas dataframe, dataframe with all encounters
    return:
        - first_encounter_df: pandas dataframe, dataframe with only the first encounter for a given patient
    '''
    # encounter_id order is the time order, so the first encounter of a patient is the smallest id.
    first_ids = df.groupby('patient_nbr')['encounter_id'].min()
    # Keep *all* lines of that encounter (not just one row): the lines hold the drugs of the encounter
    # that are aggregated in the next step.
    first_encounter_df = df[df['encounter_id'].isin(first_ids.values)].copy()
    first_encounter_df = first_encounter_df.sort_values(['patient_nbr', 'encounter_id']).reset_index(drop=True)
    return first_encounter_df


# ----------------------------------------------------------------------------------------------
# Clinically justified cohort filtering and diagnosis (ICD-9) grouping
# ----------------------------------------------------------------------------------------------
# discharge_disposition_id values (see data_schema_references/IDs_mapping.csv)
EXPIRED_OR_HOSPICE_DISCHARGE_IDS = [11, 13, 14, 19, 20, 21]   # expired, hospice (home / medical facility), expired (Medicaid hospice)
NEONATE_DISCHARGE_IDS = [10]                                  # neonate discharged to another hospital
NEWBORN_ADMISSION_TYPE_IDS = [4]                              # newborn admission


def filter_eligible_encounters(df):
    '''
    Apply the clinical eligibility filters for a diabetes drug trial to an encounter-level (or line-level) dataframe.
    Rows are removed when ANY of these hold; the reason for each is documented in the notebook:
      - the encounter ended in death or hospice: the stay was ended by the outcome, not by treatment, and these
        patients cannot complete a 5-7 day in-hospital protocol with adherence training;
      - newborn admission / neonate transfer: not an adult type 2 diabetes population;
      - gender "Unknown/Invalid": an invalid demographic record that also cannot be audited in the bias analysis.
    return:
        - filtered dataframe, and a dataframe with the number of removed encounters per rule
    '''
    rules = {
        'expired or hospice discharge': df['discharge_disposition_id'].isin(EXPIRED_OR_HOSPICE_DISCHARGE_IDS),
        'newborn admission / neonate discharge': (df['admission_type_id'].isin(NEWBORN_ADMISSION_TYPE_IDS)
                                                  | df['discharge_disposition_id'].isin(NEONATE_DISCHARGE_IDS)),
        'gender Unknown/Invalid': df['gender'] == 'Unknown/Invalid',
    }
    report, drop = [], pd.Series(False, index=df.index)
    for name, mask in rules.items():
        report.append({'rule': name, 'encounters_matching': int(df.loc[mask, 'encounter_id'].nunique()),
                       'additionally_removed': int(df.loc[mask & ~drop, 'encounter_id'].nunique())})
        drop = drop | mask
    return df[~drop].copy().reset_index(drop=True), pd.DataFrame(report)


def icd9_group(code):
    '''
    Map an ICD-9-CM code (e.g. "250.83", "V27", "E812", "?") to its clinical chapter / group. This reduces the
    ~700 primary and the thousands of secondary codes to ~20 clinically meaningful categories.
    Diabetes (250.xx) gets its own group because it is the condition the drug targets.
    '''
    code = str(code).strip()
    if code in ('', '?', 'nan', 'None'):
        return 'unknown'
    if code[0] in 'Vv':
        return 'supplementary_V'
    if code[0] in 'Ee':
        return 'external_cause_E'
    try:
        n = float(code)
    except ValueError:
        return 'unknown'
    if 250 <= n < 251:
        return 'diabetes'
    bounds = [(140, 'infectious_parasitic'), (240, 'neoplasms'), (280, 'endocrine_metabolic_other'),
              (290, 'blood'), (320, 'mental'), (390, 'nervous_sense'), (460, 'circulatory'),
              (520, 'respiratory'), (580, 'digestive'), (630, 'genitourinary'), (680, 'pregnancy'),
              (710, 'skin'), (740, 'musculoskeletal'), (760, 'congenital'), (780, 'perinatal'),
              (800, 'symptoms_ill_defined'), (1000, 'injury_poisoning')]
    for upper, name in bounds:
        if n < upper:
            return name
    return 'unknown'


def add_diagnosis_group_features(df):
    '''
    Adds clinical groupings of the diagnoses (ICD-9 chapters):
      primary_diagnosis_group  - group of primary_diagnosis_code
      secondary_dx_group_1/2   - groups of the two pipe-delimited codes in other_diagnosis_codes
    Because the secondary codes are an unordered pair in the source, the two groups are stored in alphabetical order
    so that ("circulatory", "diabetes") and ("diabetes", "circulatory") become the same representation.
    '''
    df = df.copy()
    df['primary_diagnosis_group'] = df['primary_diagnosis_code'].apply(icd9_group)
    pair = df['other_diagnosis_codes'].astype(str).str.split('|', expand=True).reindex(columns=[0, 1])
    groups = pair.apply(lambda col: col.apply(icd9_group))
    ordered = np.sort(groups.values.astype(str), axis=1)
    df['secondary_dx_group_1'] = ordered[:, 0]
    df['secondary_dx_group_2'] = ordered[:, 1]
    return df


#Question 6
def patient_dataset_splitter(df, patient_key='patient_nbr', seed=42):
    '''
    df: pandas dataframe, input dataset that will be split
    patient_key: string, column that is the patient id

    return:
     - train: pandas dataframe,
     - validation: pandas dataframe,
     - test: pandas dataframe,
    '''
    # Split on unique patients (not on rows) so that no patient can appear in two partitions.
    rng = np.random.RandomState(seed)
    patient_ids = rng.permutation(df[patient_key].unique())
    n = len(patient_ids)
    n_train = int(round(0.6 * n))
    n_val = int(round(0.2 * n))

    train_ids = patient_ids[:n_train]
    val_ids = patient_ids[n_train:n_train + n_val]
    test_ids = patient_ids[n_train + n_val:]

    train = df[df[patient_key].isin(train_ids)].reset_index(drop=True)
    validation = df[df[patient_key].isin(val_ids)].reset_index(drop=True)
    test = df[df[patient_key].isin(test_ids)].reset_index(drop=True)
    return train, validation, test


#Question 7

def create_tf_categorical_feature_cols(categorical_col_list,
                              vocab_dir='./diabetes_vocab/'):
    '''
    categorical_col_list: list, categorical field list that will be transformed with TF feature column
    vocab_dir: string, the path where the vocabulary text files are located
    return:
        output_tf_list: list of TF feature columns
    '''
    output_tf_list = []
    for c in categorical_col_list:
        vocab_file_path = os.path.join(vocab_dir,  c + "_vocab.txt")
        # default_value=0 sends any value not seen in the training vocabulary to the placeholder
        # row that write_vocabulary_file puts first in every vocab file.
        tf_categorical_feature_column = tf.feature_column.categorical_column_with_vocabulary_file(
            key=c, vocabulary_file=vocab_file_path, default_value=0)

        vocab_size = 0
        if os.path.exists(vocab_file_path):
            with open(vocab_file_path) as f:
                vocab_size = sum(1 for _ in f)

        if vocab_size > EMBEDDING_VOCAB_THRESHOLD:
            # High cardinality (e.g. ICD-9 primary diagnosis): a dense embedding instead of
            # hundreds of one-hot columns.
            dimension = int(round(vocab_size ** 0.25 * 2))
            tf_categorical_feature_column = tf.feature_column.embedding_column(
                tf_categorical_feature_column, dimension=dimension)
        else:
            tf_categorical_feature_column = tf.feature_column.indicator_column(
                tf_categorical_feature_column)
        output_tf_list.append(tf_categorical_feature_column)
    return output_tf_list


#Question 8
def normalize_numeric_with_zscore(col, mean, std):
    '''
    This function can be used in conjunction with the tf feature column for normalization
    '''
    return (col - mean)/std



def create_tf_numeric_feature(col, MEAN, STD, default_value=0):
    '''
    col: string, input numerical column name
    MEAN: the mean for the column in the training data
    STD: the standard deviation for the column in the training data
    default_value: the value that will be used for imputing the field

    return:
        tf_numeric_feature: tf feature column representation of the input field
    '''
    # A constant column in the training data has std 0 (or NaN); avoid dividing by it.
    mean = float(MEAN)
    std = float(STD) if (STD is not None and not np.isnan(STD) and STD > 0) else 1.0

    def normalizer(x):
        # numeric_column applies normalizer_fn *before* its own cast to float32, so integer
        # columns (e.g. num_medications) arrive here as int64 tensors. Cast first, then z-score.
        return normalize_numeric_with_zscore(tf.cast(x, tf.float32), mean, std)

    tf_numeric_feature = tf.feature_column.numeric_column(
        key=col, default_value=default_value, normalizer_fn=normalizer)
    return tf_numeric_feature

#Question 9
def get_mean_std_from_preds(diabetes_yhat):
    '''
    diabetes_yhat: TF Probability prediction object
    '''
    m = diabetes_yhat.mean()
    s = diabetes_yhat.stddev()
    return m, s

# Question 10
def get_student_binary_prediction(df, col, threshold=CUTOFF_DAYS):
    '''
    df: pandas dataframe prediction output dataframe
    col: str,  probability mean prediction field
    threshold: number of days of expected stay at or above which the patient is selected
    return:
        student_binary_prediction: pandas dataframe converting input to flattened numpy array and binary labels
    '''
    student_binary_prediction = (np.asarray(df[col]).flatten() >= threshold).astype(int)
    return student_binary_prediction
