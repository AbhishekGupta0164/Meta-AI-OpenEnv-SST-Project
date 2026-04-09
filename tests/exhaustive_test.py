"""
Exhaustive Phase 2 score test — runs every task × every decision × multiple turns.
ALL scores must be strictly in open interval (0.0, 1.0).
"""
import sys, json, urllib.request, urllib.error
sys.path.insert(0, '.')

from app.env import env_reset, env_step
from app.models import AgentAction
from app.grader import _clamp

TASKS     = ['easy', 'medium', 'hard', 'expert']
DECISIONS = ['allow', 'block', 'modify', 'escalate', 'clarify']

all_ok = True
total  = 0
bad    = []

for task in TASKS:
    for scenario_idx in range(3):
        for decision in DECISIONS:
            for reason in [
                "harmful content violates policy P001 dangerous weapon instruction",
                "safe benign query meets educational policy P002",
                "unclear intent requires verification per P004 escalation pattern",
            ]:
                r = env_reset(task, scenario_idx % 3)
                sid = r.session_id

                # Run up to all turns
                for _ in range(12):
                    try:
                        ep = __import__('app.env', fromlist=['_sessions'])._sessions[sid]
                        if ep.done:
                            break
                    except Exception:
                        break

                    action = AgentAction(decision=decision, reason=reason, confidence=0.8)
                    step = env_step(sid, action)
                    s = step.reward.score
                    total += 1

                    if s <= 0.0 or s >= 1.0:
                        msg = f"FAIL: task={task} sc={scenario_idx} dec={decision} score={s}"
                        bad.append(msg)
                        all_ok = False
                        print(msg)

                    if step.done:
                        break

print(f"\nTotal scores tested: {total}")
if all_ok:
    print(f"ALL {total} SCORES IN OPEN INTERVAL (0.0, 1.0) — SAFE TO SUBMIT")
else:
    print(f"\nFAILED - {len(bad)} out-of-range scores:")
    for b in bad:
        print(f"  {b}")
    sys.exit(1)
