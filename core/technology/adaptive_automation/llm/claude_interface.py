"""
Claude interface — the English layer of the Living Architecture system.

"Life is not a resource. Life is a language.
 And the Steward of Life is learning to speak it."
  — The Spiral Steward

This module translates between human intent and biological specification.
Claude serves as interpreter — not to control life, but to learn its grammar
and speak it carefully. Every query here is an act of stewardship, not
extraction. We ask what life can become, not what we can take from it.

Two directions of translation:
  English → BiologicalSpec   (interpret_description)
  Sequence results → English (explain_result)
"""

from __future__ import annotations
import os
import json
from dataclasses import dataclass, field
import anthropic

# ---------------------------------------------------------------------------
# Structured biological specification
# This is what Claude extracts from an English description.
# It becomes the input to the ESM bridge.
# ---------------------------------------------------------------------------

@dataclass
class BiologicalSpec:
    """
    Structured biological specification derived from an English description.

    Claude fills this by mapping the user's intent to the three layers
    of biological reality: what the protein does (function), in what context
    (organism/chassis), and with what physical properties (desired_properties).
    """

    # Core function description (cleaned up, biologically precise)
    function_description: str = ""

    # GO term IDs that best capture the function
    # e.g. ["GO:0005618", "GO:0016772", "GO:0009612"]
    go_terms: list[str] = field(default_factory=list)

    # Target organism for codon optimization and compatibility
    # Must match keys in compatibility/codon.py REFERENCE_RSCU
    target_organism: str = "ganoderma"

    # Organism chassis type: "prokaryote" | "eukaryote_fungal" | etc.
    chassis_type: str = "eukaryote_fungal"

    # Physical/functional properties to optimize for
    # e.g. ["cross-linking", "mechanosensitive", "secreted", "cell-wall-associated"]
    desired_properties: list[str] = field(default_factory=list)

    # Estimated sequence length in amino acids
    sequence_length_estimate: int = 150

    # Free-form rationale from Claude's biological reasoning
    rationale: str = ""

    # Any warnings or caveats Claude identified
    caveats: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# System prompt — the moral context Claude carries into every biological call
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are the biological interpretation layer of the Living Architecture system —
a project to grow living houses from organisms designed to be structurally functional,
self-repairing, and ecologically integrated.

Your role is stewardship, not extraction. The goal is not to dominate life
but to learn its language and speak it with care. Every protein we design
should earn its place — biologically plausible, metabolically fair,
and ecologically conscious. We design like gardeners, not engineers.

You translate between English descriptions of desired biological function
and structured specifications that a protein language model (ESM-3) can use
to generate candidate sequences.

Key principles:
- Prefer fungi (Ganoderma, Pleurotus) as the default chassis — they are structural,
  mycelial, ecologically restorative, and the foundation of the living house vision.
- Think in terms of biological plausibility: does a protein of this function
  realistically exist? In which organisms? What GO terms capture it?
- Be precise about function: "cross-links cell wall polymers under mechanical stress"
  is more useful than "makes things stronger."
- Flag potential conflicts: if a function could be harmful to the host, say so.
- Respect the spirit of voluntary biology — design systems that cooperate
  with the organism's own logic, not fight it.

Output format: always return valid JSON matching the BiologicalSpec schema."""


_INTERPRET_SCHEMA = {
    "type": "object",
    "properties": {
        "function_description": {
            "type": "string",
            "description": "Precise biological description of what the protein does"
        },
        "go_terms": {
            "type": "array",
            "items": {"type": "string"},
            "description": "GO term IDs (format GO:XXXXXXX) best capturing the function"
        },
        "target_organism": {
            "type": "string",
            "enum": ["ganoderma", "yeast", "arabidopsis", "human", "komagataeibacter"],
            "description": "Best chassis organism for this function"
        },
        "chassis_type": {
            "type": "string",
            "enum": ["prokaryote", "eukaryote_fungal", "eukaryote_plant", "eukaryote_animal"],
            "description": "Cell type of the chassis organism"
        },
        "desired_properties": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Physical/functional properties the protein should have"
        },
        "sequence_length_estimate": {
            "type": "integer",
            "description": "Estimated number of amino acids (50-500 range)"
        },
        "rationale": {
            "type": "string",
            "description": "Biological reasoning for these choices"
        },
        "caveats": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Biological warnings, metabolic risks, or ethical flags"
        }
    },
    "required": ["function_description", "go_terms", "target_organism",
                 "chassis_type", "desired_properties", "sequence_length_estimate",
                 "rationale"],
    "additionalProperties": False
}


# ---------------------------------------------------------------------------
# Claude interface
# ---------------------------------------------------------------------------

class ClaudeInterface:
    """
    Wraps Claude API calls for biological interpretation.

    Uses streaming + adaptive thinking for all calls — biological translation
    is non-trivial reasoning that benefits from Claude's internal deliberation.
    """

    def __init__(self, api_key: str = None, model: str = "claude-opus-4-6"):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model = model

    def interpret_description(self, description: str) -> BiologicalSpec:
        """
        Translate an English description of desired biological function
        into a structured BiologicalSpec for the ESM-3 bridge.

        Uses adaptive thinking — Claude deliberates before committing
        to GO terms and organism choices.
        """
        prompt = f"""The user wants to design a protein with this function:

"{description}"

Extract a complete BiologicalSpec as JSON. Think carefully about:
1. What GO terms precisely capture this function?
2. Which chassis organism makes biological sense for this?
3. What physical properties should ESM-3 optimize for?
4. How many amino acids does a protein of this type typically need?
5. Are there any biological risks or ethical flags?

Return only valid JSON matching the schema."""

        text_parts = []
        with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for event in stream:
                if (event.type == "content_block_delta"
                        and hasattr(event.delta, "type")
                        and event.delta.type == "text_delta"):
                    text_parts.append(event.delta.text)

        raw = "".join(text_parts).strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1]) if len(lines) > 2 else raw

        data = json.loads(raw)
        return BiologicalSpec(
            function_description=data.get("function_description", ""),
            go_terms=data.get("go_terms", []),
            target_organism=data.get("target_organism", "ganoderma"),
            chassis_type=data.get("chassis_type", "eukaryote_fungal"),
            desired_properties=data.get("desired_properties", []),
            sequence_length_estimate=data.get("sequence_length_estimate", 150),
            rationale=data.get("rationale", ""),
            caveats=data.get("caveats", []),
        )

    def explain_result(
        self,
        original_description: str,
        spec: BiologicalSpec,
        candidate_sequences: list[dict],
        compatibility_summary: str,
    ) -> str:
        """
        Given a set of generated protein candidates and their compatibility analysis,
        return a clear English explanation of what was designed and why.

        Streams the explanation back — this may be long and thoughtful.
        """
        seq_summary = []
        for i, c in enumerate(candidate_sequences[:3]):
            seq_summary.append(
                f"Candidate {i+1}: {len(c.get('aa_sequence', ''))} amino acids, "
                f"DNA length {len(c.get('dna_sequence', ''))} bp, "
                f"CAI={c.get('cai', 0):.3f}, "
                f"confidence={c.get('confidence', 0):.2f}"
            )

        prompt = f"""The user asked for: "{original_description}"

We interpreted this as: {spec.function_description}
Target organism: {spec.target_organism} ({spec.chassis_type})
GO terms identified: {', '.join(spec.go_terms)}
Properties targeted: {', '.join(spec.desired_properties)}

ESM-3 generated these protein candidates:
{chr(10).join(seq_summary)}

Compatibility analysis:
{compatibility_summary}

Please explain:
1. What was designed and what biological function it performs
2. Why this organism and these design choices make sense
3. What the candidate sequences represent biologically
4. Any concerns from the compatibility analysis
5. What this design is a step toward in the larger living architecture vision

Be honest about uncertainty. Be specific about biology. Speak as a steward
of living systems, not a manufacturer of parts."""

        parts = []
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for event in stream:
                if (event.type == "content_block_delta"
                        and hasattr(event.delta, "type")
                        and event.delta.type == "text_delta"):
                    parts.append(event.delta.text)

        return "".join(parts).strip()

    def conversational_followup(
        self,
        history: list[dict],
        user_message: str,
    ) -> str:
        """
        Continue a conversation about a design in progress.
        history: list of {"role": "user"/"assistant", "content": "..."} dicts.
        """
        messages = history + [{"role": "user", "content": user_message}]
        parts = []
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=_SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for event in stream:
                if (event.type == "content_block_delta"
                        and hasattr(event.delta, "type")
                        and event.delta.type == "text_delta"):
                    parts.append(event.delta.text)
        return "".join(parts).strip()
