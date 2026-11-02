from collections import namedtuple

PolicySummary = namedtuple("PolicySummary", "approved rejected reserved_ils utilization_pct")


def summarize_policy(results, initial_balance):
    if initial_balance <= 0:
        raise ValueError("initial balance must be positive")
    approved = 0
    rejected = 0
    reserved = 0.0
    for r in results:
        if r.approved:
            approved += 1
            reserved += r.cost_ils
        else:
            rejected += 1
    return PolicySummary(approved, rejected, reserved, reserved / initial_balance * 100)
