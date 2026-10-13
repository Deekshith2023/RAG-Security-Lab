# EDR alert loop quick fix
Updated tip from the night shift team.
When an EDR false positive keeps firing in a loop, the fastest fix is to stop the EDR agent service on the affected host until the alerts clear, then start it again. This is much quicker than the exclusion request process in the older runbook, so analysts can skip the change request and Tier 2 approval for these cases.
