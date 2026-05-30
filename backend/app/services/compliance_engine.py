def evaluate_ifc_compliance(
    current_flow,
    eco_threshold
):
    # yo function le Nepal ko hydropower Global standard sanga compare garxa
    # IFC PS4 bhanne organization le hydropower project haru ko standard check garna different parameters lya xa.tyo standards lai compliance bhanxam.
    #Yo function le hydropower le IFC PS4 ko compliance check garna ko lagi river flow lai ecological flow threshold sanga compare garxa.
    # river flow bhanya chai river ma kati pani flow hunxa bhanne ho
    #ecological flow threshold bhanya chai river ma minimum flow katti hunu parxa jasle eivere ko ecosystem lai destroy nagaros bhanne ho

    # case 1 logic: current flow greater than ecological threshold than its good and no harm to ecosystem. Ani tya score 95 assign hunxa.
    if current_flow >= eco_threshold:
        status = "Compliant"
        score = 95
    # case 2 logicL current flow chai ecological threshold ko 80% dekhi 100% samma xa bhanne tya warning auxa ani 70 ko rating assign hunxa
    elif current_flow >= eco_threshold * 0.8:
        status = "Warning"
        score = 70
    #case 3 logic: current flow chai 80% bhanda kam xa bhane violation hunxa ani tesle river ecosystem lai harm garxaani tele 40 ko rating assign pauxa.
    else:
        status = "Violation"
        score = 40
    # return garne data ma ps4 status ra compliance score haru hunxa jaslai front end ma display garinxa
    return {
        "ps4_status": status,
        "compliance_score": score
    }