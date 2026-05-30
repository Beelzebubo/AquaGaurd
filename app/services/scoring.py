def calculate_esg_score(
    compliance_score,
    anomaly_detected
):
# final calculations for the ESG (environmental, social, and governance) score
# yo chai based on compliance score and anomaly detection result
# yo 2 parameters lai use garera final ESG score calculate garinxa

#eg: compliance score 80 xa bhane, initial ESC is also 80
# ani anomaly detect bha xa bhane 15 points deduction garinxa max ESC bata.
# so nepal ko ESG score 65 hunxa (80 - 15 = 65) if anomaly detected, otherwise it remains 80 tara hamlai tha xa tyo 60 ni xaina.
# for proof yo maile google bat utha:Nepal does not have a single standardized ESG (Environmental, Social, and Governance) score, 
    # but rather varying assessments from different global indices. Overall, the country generally ranks in the middle to lower tier globally,
    # boasting low environmental impact but facing notable governance and institutional challenges
    score = compliance_score

    if anomaly_detected:
        score -= 15
# yelle ESG score lai -ve ma aye 0 set garxa ani return gardinxa.
    return max(score, 0)