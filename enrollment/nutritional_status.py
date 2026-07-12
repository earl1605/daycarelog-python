# WHO weight-for-age median-table classification, ported from the sibling
# Spring Boot + React DaycareLog project (web/src/utils/nutritionalStatus.js /
# NutritionalStatusCalculator.java) so both course deliverables classify the
# same weight/age/sex inputs identically.

MEDIAN_WEIGHT_KG = {
    "M": [3.3, 4.5, 5.6, 6.4, 7.0, 7.5, 7.9, 8.3, 8.6, 8.9, 9.2, 9.4, 9.6, 10.0, 10.3,
          10.6, 10.9, 11.1, 11.4, 11.6, 11.8, 12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2,
          13.4, 13.6, 13.8, 14.0, 14.2, 14.4, 14.6, 14.8, 14.9, 15.1, 15.3, 15.5, 15.7,
          15.9, 16.1, 16.2, 16.4, 16.6, 16.8, 17.0, 17.2, 17.4, 17.5, 17.7, 17.9, 18.1,
          18.3, 18.5, 18.7, 18.9, 19.1, 19.3, 19.5],
    "F": [3.2, 4.2, 5.1, 5.8, 6.4, 6.9, 7.3, 7.6, 7.9, 8.2, 8.5, 8.7, 8.9, 9.2, 9.5,
          9.8, 10.0, 10.2, 10.5, 10.7, 10.9, 11.1, 11.3, 11.5, 11.7, 11.9, 12.1, 12.3,
          12.5, 12.7, 12.9, 13.1, 13.3, 13.5, 13.7, 13.9, 14.1, 14.2, 14.4, 14.6, 14.8,
          15.0, 15.1, 15.3, 15.5, 15.7, 15.9, 16.1, 16.2, 16.4, 16.6, 16.8, 17.0, 17.2,
          17.4, 17.6, 17.8, 18.0, 18.2, 18.4, 18.6],
}

STATUS_LABELS = {
    "NORMAL": "Normal",
    "UNDERWEIGHT": "Underweight",
    "SEVERELY_UNDERWEIGHT": "Severely Underweight",
    "OVERWEIGHT": "Overweight",
}


def age_in_months(date_of_birth, as_of):
    return (as_of.year - date_of_birth.year) * 12 + (as_of.month - date_of_birth.month)


def classify_nutritional_status(weight_kg, date_of_birth, sex, as_of):
    """Returns (code, label) such as ("NORMAL", "Normal"), or (None, None)
    when the record can't be classified (missing weight/DOB or age out of
    the 0-60 month WHO table range)."""
    if weight_kg is None or date_of_birth is None:
        return None, None
    months = age_in_months(date_of_birth, as_of)
    if months < 0 or months > 60:
        return None, None

    table = MEDIAN_WEIGHT_KG["F"] if sex == "F" else MEDIAN_WEIGHT_KG["M"]
    median = table[min(months, 60)]
    ratio = float(weight_kg) / median

    if ratio >= 1.20:
        return "OVERWEIGHT", STATUS_LABELS["OVERWEIGHT"]
    if ratio >= 0.90:
        return "NORMAL", STATUS_LABELS["NORMAL"]
    if ratio >= 0.75:
        return "UNDERWEIGHT", STATUS_LABELS["UNDERWEIGHT"]
    return "SEVERELY_UNDERWEIGHT", STATUS_LABELS["SEVERELY_UNDERWEIGHT"]
