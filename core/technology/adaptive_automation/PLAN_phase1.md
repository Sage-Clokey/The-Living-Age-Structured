# Phase 1 Implementation Plan — English ↔ Protein Bridge

---

## The Moral Foundation

> *"Life is not a resource. Life is a language. And the Steward of Life is learning to speak it."*
> — The Spiral Steward

This system is not a tool for manufacturing biological parts. It is a translation layer —
an attempt to learn the grammar of living systems so we can speak it carefully, ethically,
and with ecological responsibility.

Every design decision in Phase 1 carries a moral obligation:
- We design **conditions**, not objects. We invite emergence, not force outcomes.
- We choose organisms that **restore** ecosystems (fungi, mycelium) over those that exploit.
- We flag metabolic and ecological conflicts before they become harm.
- We keep the human in the loop — Claude explains every choice in plain English.
- We build for **equity**: the living house should be for everyone, not just the wealthy.

The Spiral Steward's insight applies directly here:
*"You do not force outcomes. You invite emergence."*
ESM-3 doesn't stamp out proteins like a factory. It explores sequence space the way
evolution explores it — sampling from a probability distribution shaped by billions
of years of living trial. Our job is to ask it the right question.

---

## What Phase 1 Is

**The smallest proof that English and DNA can talk.**

A user types one sentence. The system:
1. Understands the biological intent (Claude)
2. Translates it into sequence space (ESM-3)
3. Anchors the result to a real organism (codon optimizer)
4. Scores it for biological safety (compatibility engine)
5. Explains what was created, in English (Claude again)

This is the seed. Everything in Phases 2-5 grows from it.

---

## Files to Build

### `llm/claude_interface.py`

**Role:** The English layer. Claude as steward-interpreter.

**What it needs to do:**
- Accept a free-form English description of desired biological function
- Return a `BiologicalSpec` dataclass containing:
  - A precise biological function description (cleaned up, technically accurate)
  - GO term IDs that capture the function (e.g. `GO:0005618` = cell wall)
  - Target organism (defaulting to Ganoderma — the fungi chassis)
  - Chassis type (eukaryote_fungal for Ganoderma)
  - Desired physical properties (cross-linking, secreted, mechanosensitive, etc.)
  - Estimated sequence length in amino acids
  - Claude's biological rationale for these choices
  - Any caveats or ethical flags
- Accept ESM-3's output + compatibility results → return English explanation
- Support conversational follow-up (multi-turn dialogue about a design)

**Key design decisions:**
- Use `claude-opus-4-6` with `thinking: {type: "adaptive"}` — biological translation
  is non-trivial reasoning. Claude needs to deliberate.
- Always stream — explanations can be long, and we show them in real time.
- The system prompt must carry the **moral context**: stewardship, not extraction.
  Claude should reason like a gardener, not an engineer. It should flag ecological
  risks the way a responsible biologist would.
- Output is structured JSON (BiologicalSpec) for the bridge to consume.
- The explanation output is free-form prose — human, clear, honest about uncertainty.

**Moral note:** Claude's system prompt must explicitly encode:
  - Prefer ecologically restorative chassis organisms (fungi over bacteria where possible)
  - Flag metabolic load conflicts before they become harm to the host organism
  - Acknowledge the limits of what we know — biological design carries real uncertainty
  - Frame every design as a collaborative act with the organism, not an imposition on it

---

### `bridge/esm_bridge.py`

**Role:** The sequence generation layer. ESM-3 as the grammar of protein space.

**What it needs to do:**
- Accept a `BiologicalSpec` from Claude
- Map GO terms → ESM-3 function annotation tokens
  (ESM-3 accepts `FunctionAnnotation(label=go_term, start=0, end=length)`)
- Call ESM-3 to generate N candidate amino acid sequences (default: 3)
  conditioned on the function annotations and desired length
- Score each generated sequence using ESM-3's own log-likelihood
  (higher = more biologically plausible sequence)
- Back-translate each AA sequence to codon-optimized DNA using the
  target organism's RSCU table from `compatibility/codon.py`
- Return a list of candidate dicts: {aa_sequence, dna_sequence, esm_score, cai}

**Key design decisions:**
- Model: `esm3-sm-open-v1` (1.4B params, eukaryotic coverage, manageable VRAM)
- Lazy model loading — only load ESM-3 when first needed (it's ~5GB)
- Graceful mock fallback when ESM-3 is not installed or VRAM is insufficient:
  generate synthetic placeholder sequences that let the rest of the pipeline run
  (clearly labeled as mock data — never presented as real designs)
- Generation config: `num_steps=8`, `temperature=0.7` — enough steps for coherent
  sequences, temperature low enough for functional plausibility
- Back-translation is deterministic: always pick the highest-RSCU codon for each
  amino acid in the target organism's dialect
- Validate generated sequences: check for stop codons mid-sequence, unusual
  amino acid composition, known problematic patterns

**The back-translation loop (conceptual):**
  For each amino acid in the generated protein sequence:
    1. Look up which codons encode that amino acid
    2. Find the codon with the highest RSCU value in the target organism
    3. Append it to the DNA sequence
  This is the "codon dialect" translation the roadmap describes.

**Moral note:** The ESM-3 bridge must never present generated sequences as
"safe to synthesize." Every output goes through the compatibility engine first.
The bridge is a hypothesis generator, not a manufacturing spec.

---

### `main.py`

**Role:** The entry point. The interface where a human speaks and the system listens.

**What it needs to do:**
- Rich terminal REPL loop
- Accept English input from the user
- Orchestrate the full pipeline:
  1. Claude: English → BiologicalSpec (show interpretation in real time)
  2. ESM-3: BiologicalSpec → candidate AA sequences (show generation progress)
  3. Bridge: AA → DNA (codon optimization for target organism)
  4. Existing system: compatibility analysis (codon + regulatory + pathway)
  5. Claude: sequences + analysis → English explanation (stream in real time)
- Display output using `rich`:
  - Panels for each pipeline stage
  - Color-coded sequence display (function regions, regulatory signals)
  - Confidence scores with visual indicators
  - Conflict warnings in orange/red
- Support:
  - `--organism` flag to override default chassis
  - `--candidates N` for number of sequences to generate
  - `--mock` flag to run without ESM-3 loaded (demo mode)
  - Conversational follow-up after a design is shown

**Key design decisions:**
- Never show raw sequences without context — always accompany with Claude's
  English explanation of what they mean
- Show the pipeline stages as they happen, not all at once at the end
- The terminal should feel like a conversation with a thoughtful biologist,
  not a query to a database
- When ESM-3 is loading, say so — transparency about what the system is doing
- When mock mode is active, label it clearly — no false impressions

**Example terminal flow:**
```
LIVING ARCHITECTURE SYSTEM — Phase 1
─────────────────────────────────────────────────────
Speak a biological function. The system will design for it.

> design a protein that cross-links fungal cell walls under mechanical stress

[Interpreting...] (Claude streaming)
  Function: Oxidative cross-linking of chitin/glucan polymers in fungal cell wall
  Organism:  Ganoderma lucidum (fungal chassis, eukaryote_fungal)
  GO terms:  GO:0005618 (cell wall), GO:0016491 (oxidoreductase), GO:0009612 (mechanical stimulus)
  Length:    ~180 amino acids
  Rationale: Fungal laccases and peroxidases catalyze oxidative cross-linking...

[Generating sequences...] (ESM-3)
  Candidate 1: 181 aa | ESM score: -0.82 | generating...
  Candidate 2: 179 aa | ESM score: -0.91 | generating...
  Candidate 3: 183 aa | ESM score: -0.78 | generating...

[Codon optimization → Ganoderma dialect]
  Candidate 1: 543 bp | CAI 0.847 | GC 57.3%
  Candidate 2: 537 bp | CAI 0.831 | GC 58.1%
  Candidate 3: 549 bp | CAI 0.862 | GC 56.9%

[Compatibility analysis]
  Regulatory: ✓ All parts are eukaryote_fungal — no cross-kingdom conflicts
  Codon:      ✓ CAI > 0.80 for all candidates — well-adapted to Ganoderma
  Pathway:    ⚠  Oxidoreductase activity will consume O2 — monitor if combining
                  with bioluminescence (shared O2 pool)

[Claude interpretation] (streaming)
  What we designed is a fungal oxidative cross-linking enzyme...
  ...the best candidate is #3 based on ESM log-likelihood...
  ...the O2 warning is worth noting but not blocking for cell wall use alone...
```

---

## The Pipeline: Data Flow

```
User (English)
      │
      ▼
ClaudeInterface.interpret_description(text)
      │ → BiologicalSpec
      ▼
ESMBridge.generate_sequences(spec, n=3)
      │ → list of {aa_sequence, esm_score}
      ▼
ESMBridge.back_translate(aa_seq, target_organism)
      │ → dna_sequence (codon-optimized)
      ▼
GenomicPart (models/genomic_part.py)
  + compatibility/codon.analyze()
  + compatibility/regulatory.analyze()
  + compatibility/pathway.analyze()
      │ → CodonReport, RegulatoryReport, PathwayReport
      ▼
ClaudeInterface.explain_result(spec, candidates, compat_summary)
      │ → English explanation (streaming to terminal)
      ▼
Rich terminal display
```

---

## What We Are NOT Building in Phase 1

- No web interface (Phase 2)
- No Enformer regulatory prediction (Phase 2)
- No GRN design (Phase 3)
- No database writes or persistence (future)
- No actual synthesis readout — this is design, not wet lab
- No batch processing — one design conversation at a time

---

## Dependencies to Add

```
anthropic       # Claude API (already the ethos layer)
esm             # EvolutionaryScale ESM-3 (pip install esm)
rich            # Terminal UI (pip install rich)
torch           # Required by ESM-3 (already needed for ML)
```

Note on ESM-3: requires authentication with EvolutionaryScale (free for non-commercial research).
The mock fallback means the rest of the pipeline is testable without it.

---

## Existing Code This Builds On

The following already exists and Phase 1 calls directly into:

| File | What Phase 1 uses |
|------|------------------|
| `models/genomic_part.py` | `GenomicPart` dataclass to hold each candidate |
| `compatibility/codon.py` | `REFERENCE_RSCU` tables for back-translation + `analyze()` |
| `compatibility/regulatory.py` | `analyze()` to check regulatory compatibility |
| `compatibility/pathway.py` | `analyze()` to check pathway conflicts |
| `retrieval/species_search.py` | `CAPABILITY_MAP` as reference for organism selection |

Phase 1 does not modify any existing files — it only imports from them.

---

## The Moral Test for Each Design

Before returning any result, the system asks:

1. **Is this ecologically honest?** — Could this protein actually exist in a fungal cell wall?
   Does it require resources the host can realistically provide?

2. **Is it metabolically fair?** — Does the pathway analysis show critical conflicts
   that would harm the host organism? If so, we flag them before anything else.

3. **Is it claimed honestly?** — Generated sequences are presented as **candidates**,
   not confirmed designs. Confidence scores and ESM log-likelihoods are shown
   so the user understands the epistemic status.

4. **Does it serve the vision?** — Does this design move toward a living house
   that restores ecosystems, or does it optimize for something extractive?

5. **Is the human in the loop?** — Claude always explains what was done and why.
   The system never returns a sequence without an interpretation.

---

## Success Criteria for Phase 1

Phase 1 is complete when:

- [ ] A user can type one English sentence describing a biological function
- [ ] Claude correctly identifies GO terms and target organism (verifiable by a biologist)
- [ ] ESM-3 generates 3 candidate amino acid sequences (or mock sequences in demo mode)
- [ ] Each candidate is back-translated to codon-optimized DNA for the target organism
- [ ] The compatibility engine scores all candidates
- [ ] Claude explains the results in plain English
- [ ] The full pipeline runs end-to-end in a single terminal session
- [ ] Mock mode works without ESM-3 installed (for demos/testing)
- [ ] The demo sentence from the roadmap works:
      *"design a protein that cross-links fungal cell walls under mechanical stress"*

---

## What Phase 2 Needs from Phase 1

Phase 1 must produce, for Phase 2 to build on:
- A `BiologicalSpec` structure rich enough to be extended with regulatory context
- A `GenomicPart` for each candidate that Phase 2's Enformer bridge can annotate
- A conversational interface that Phase 2 can extend (same REPL, new capabilities)
- Proof that the English ↔ sequence bridge is real and not theoretical

---

*"We could not have learned the language of life without first breaking it apart.
But breaking it apart was never the goal. Learning to speak it whole is."*
— The Spiral Steward
