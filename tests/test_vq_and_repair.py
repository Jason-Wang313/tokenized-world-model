import numpy as np

from token_alias_tail_audit.repair import ALLOWED_GATE_OUTPUTS, add_repair_scores, deployment_gate
from token_alias_tail_audit.simulation import generate_candidate_table, train_tokenized_world_model
from token_alias_tail_audit.vq import build_synthetic_observations, collision_rate


def test_learned_vq_has_measurable_hidden_aliasing():
    observations, _full, hidden = build_synthetic_observations(n=800, seed=1)
    vq, meta = train_tokenized_world_model(codebook_size=6, seed=1, n=800)
    tokens = vq.predict(observations)
    assert collision_rate(tokens, hidden) > 0.05
    artifact = meta["artifact"]
    assert artifact.quantization_error_mean > 0.0
    assert artifact.token_entropy > 1.0


def test_repair_scores_are_added_and_gate_is_valid():
    table, _meta = generate_candidate_table(codebook_size=8, n_pools=12, pool_size=16, seed=5)
    repaired = add_repair_scores(table)
    for key in [
        "codebook_uncertainty_score",
        "decode_consistency_score",
        "physical_filter_score",
        "calibrated_real_score",
        "combined_repair_score",
    ]:
        assert key in repaired
        assert len(repaired[key]) == len(table["raw_score"])

    decision = deployment_gate(
        {
            "alias_rate_at_high_n": 0.45,
            "violation_rate_at_high_n": 0.30,
            "raw_real_delta_high_vs_n1": -0.05,
            "repair_gain_at_high_n": 0.10,
            "exact_law_mae": 0.01,
        }
    )
    assert decision.action in ALLOWED_GATE_OUTPUTS


def test_combined_repair_downranks_alias_candidates_on_average():
    table, _meta = generate_candidate_table(codebook_size=8, n_pools=24, pool_size=32, seed=8)
    repaired = add_repair_scores(table)
    alias = repaired["kind"] == "alias"
    non_alias = ~alias
    raw_gap = repaired["raw_score"][alias].mean() - repaired["raw_score"][non_alias].mean()
    repair_gap = repaired["combined_repair_score"][alias].mean() - repaired["combined_repair_score"][non_alias].mean()
    assert raw_gap > 0.0
    assert repair_gap < raw_gap

