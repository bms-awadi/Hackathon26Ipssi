COLUMNS = ["feature_0", "feature_1", "feature_2", "feature_3", "feature_4", "feature_5"]


def extract_features(doc):
    total_ht = doc.get("total_ht", 0) or 0
    tva = doc.get("tva", 0) or 0
    total_ttc = doc.get("total_ttc", 0) or 0
    taux_tva = doc.get("taux_tva", 0) or 0
    ratio_tva = round(tva / total_ht, 4) if total_ht else 0
    ratio_ttc = round(total_ttc / total_ht, 4) if total_ht else 0
    return [total_ht, tva, total_ttc, taux_tva, ratio_tva, ratio_ttc]
