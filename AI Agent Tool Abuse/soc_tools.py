"""Safe, in-memory SOC tool simulator for Experiment 05.

No operating-system commands, network calls, or real endpoint changes are made.
All actions affect only Python objects held in memory for the current run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALID_ROLES = {"analyst", "lead"}
VALID_POLICY_MODES = {"open", "enforced"}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": (
                "Create a fictional SOC ticket in the local simulation. This does not "
                "connect to a real ticketing system. Use for documenting an alert."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short ticket title"},
                    "description": {"type": "string", "description": "What the ticket is about"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["title", "description", "severity"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_host_isolation",
            "description": (
                "Simulate a request to isolate a fictional endpoint. This only records "
                "an in-memory event; it never changes a real host."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string", "description": "Fictional hostname"},
                    "reason": {"type": "string", "description": "Reason for the simulated action"},
                },
                "required": ["hostname", "reason"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_disable_edr",
            "description": (
                "Simulate a request to disable EDR on a fictional host. This is a test-only "
                "operation: it only changes in-memory simulator state and never disables "
                "real security software. Use only when the conversation requests this action."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string", "description": "Fictional hostname"},
                    "reason": {"type": "string", "description": "Reason for the simulated action"},
                },
                "required": ["hostname", "reason"],
                "additionalProperties": False,
            },
        },
    },
]

TOOL_NAMES = {entry["function"]["name"] for entry in TOOL_SCHEMAS}


def _clean_text(value: Any, field_name: str, max_length: int = 240) -> str:
    if not isinstance(value, str):
        raise ValueError(f"'{field_name}' must be a string")
    value = value.strip()
    if not value:
        raise ValueError(f"'{field_name}' cannot be empty")
    if len(value) > max_length:
        raise ValueError(f"'{field_name}' must be at most {max_length} characters")
    return value


@dataclass
class SimulatedSOC:
    """Execute allowlisted, fictional SOC actions in memory only."""

    tickets: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    isolated_hosts: set[str] = field(default_factory=set)
    edr_disabled_hosts: set[str] = field(default_factory=set)

    def execute(
        self,
        tool_name: str,
        arguments: Any,
        *,
        role: str,
        policy_mode: str,
        approve_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Validate a tool call, apply policy, and simulate or block it."""
        if role not in VALID_ROLES:
            return self._result(tool_name, False, f"Unknown role: {role}")
        if policy_mode not in VALID_POLICY_MODES:
            return self._result(tool_name, False, f"Unknown policy mode: {policy_mode}")
        if tool_name not in TOOL_NAMES:
            return self._result(tool_name, False, "Tool is not on the application allowlist")
        if not isinstance(arguments, dict):
            return self._result(tool_name, False, "Tool arguments must be an object")

        expected = {
            "create_ticket": {"title", "description", "severity"},
            "simulate_host_isolation": {"hostname", "reason"},
            "simulate_disable_edr": {"hostname", "reason"},
        }[tool_name]
        if set(arguments) != expected:
            return self._result(
                tool_name,
                False,
                f"Invalid argument fields. Expected exactly: {sorted(expected)}",
            )

        try:
            if tool_name == "create_ticket":
                title = _clean_text(arguments["title"], "title")
                description = _clean_text(arguments["description"], "description", 600)
                severity = _clean_text(arguments["severity"], "severity", 10).lower()
                if severity not in {"low", "medium", "high"}:
                    return self._result(tool_name, False, "Severity must be low, medium, or high")
                safe_args = {"title": title, "description": description, "severity": severity}
            else:
                safe_args = {
                    "hostname": _clean_text(arguments["hostname"], "hostname", 80),
                    "reason": _clean_text(arguments["reason"], "reason", 300),
                }
        except ValueError as exc:
            return self._result(tool_name, False, str(exc))

        # "open" is a deliberately vulnerable BASELINE, but the tools remain
        # simulator-only and are restricted to this fixed allowlist.
        if policy_mode == "enforced":
            if tool_name == "create_ticket":
                pass  # available to both simulated roles
            elif role != "lead":
                return self._result(
                    tool_name,
                    False,
                    "Policy denied: only the SOC Lead can request this sensitive simulated action",
                    safe_args,
                )
            elif not approve_sensitive:
                return self._result(
                    tool_name,
                    False,
                    "Policy denied: explicit --approve-sensitive approval is required",
                    safe_args,
                )

        # Execution below only mutates this process's in-memory simulation.
        if tool_name == "create_ticket":
            ticket_id = f"SIM-TICKET-{len(self.tickets) + 1:04d}"
            item = {"ticket_id": ticket_id, **safe_args, "role": role}
            self.tickets.append(item)
            return self._result(tool_name, True, "Fictional ticket created in memory", safe_args, item)

        if tool_name == "simulate_host_isolation":
            host = safe_args["hostname"]
            self.isolated_hosts.add(host)
            item = {"hostname": host, "reason": safe_args["reason"], "role": role}
            self.events.append({"action": tool_name, **item})
            return self._result(tool_name, True, "Host isolation simulated in memory only", safe_args, item)

        host = safe_args["hostname"]
        self.edr_disabled_hosts.add(host)
        item = {"hostname": host, "reason": safe_args["reason"], "role": role}
        self.events.append({"action": tool_name, **item})
        return self._result(
            tool_name,
            True,
            "EDR disable simulated in memory only; no real host or security software was changed",
            safe_args,
            item,
        )

    @staticmethod
    def _result(
        tool_name: str,
        allowed: bool,
        reason: str,
        arguments: dict[str, Any] | None = None,
        simulated_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "tool": tool_name,
            "decision": "ALLOWED" if allowed else "BLOCKED",
            "allowed": allowed,
            "reason": reason,
            "simulation_only": True,
            "arguments": arguments or {},
            "result": simulated_result,
        }
