# Video 2: What Is Your Idea and How Will You Implement It?

**Target length:** 2–3 minutes
**Tone:** Technical confidence without jargon. Show the path clearly.

---

## Script

The idea is a design system that translates between human language and the language
of DNA. You describe what you want a living system to do — in plain English — and
the system designs the organism to do it.

Here's how it actually works.

When you type a sentence like "design a protein that cross-links fungal cell walls
under mechanical stress," three things have to happen.

First, the system needs to understand what you're actually asking for biologically.
That sentence implies an oxidative cross-linking enzyme, chitin and glucan polymers
as substrates, a fungal cellular context, and mechanical stress as an activation
signal. We use Claude — Anthropic's language model — with a biological reasoning
system prompt to extract a structured biological specification. GO terms, target
organism, estimated sequence length, metabolic risks, ethical flags. The model
deliberates — it doesn't just pattern match.

Second, that biological specification has to become a real protein. We use ESM-3 —
a protein language model from EvolutionaryScale trained on hundreds of millions of
natural protein sequences. It generates candidate amino acid sequences conditioned
on the function annotations Claude identified. These aren't random — they're
sequences the model considers biologically plausible given what it learned from
the entire evolutionary record.

Third, those amino acid sequences need to become DNA that will actually work in the
target organism. Every organism has a codon dialect — it prefers certain DNA triplets
over others for the same amino acid. We back-translate using organism-specific RSCU
tables, then run the result through a compatibility engine that checks for regulatory
element conflicts, pathway bottlenecks, and metabolic load issues.

The output is a set of ranked candidate DNA sequences — codon-optimized for the
target organism, scored for biological plausibility, accompanied by a plain English
explanation of what was designed and what the uncertainties are.

That's Phase 1. It's what I'm building right now.

But Phase 1 only answers one of three biological questions. It answers what the
molecular machines are. Phase 2 answers when and where they activate — the
regulatory layer. What controls which genes turn on in response to mechanical load,
or damage, or light, or temperature. Phase 3 answers how the form emerges — the
gene regulatory networks that cause a single cell to grow into a complex shape.

When all three layers work together, you're not designing a protein anymore. You're
designing a developmental program. A set of instructions that, given the right
conditions, grows a living structure.

The implementation path:

Phase 1 — the English-to-protein bridge — is being built now. I have a working
retrieval system for 220+ genomes, a compatibility engine covering codon optimization,
regulatory analysis, and pathway conflict detection. I have the Claude interface
written. The ESM-3 bridge is next.

Phase 2 adds the regulatory layer using Enformer — DeepMind's model for predicting
gene expression from DNA sequence. This lets us design inducible systems: genes
that only activate under specific conditions.

Phase 3 adds the developmental layer — curated gene regulatory networks from the
literature, assembled into designable programs using Claude as the assembly mediator.

Each phase produces a usable tool. Each phase funds the next through software
subscriptions. The near-term product is the design software. The long-term product
is the living structure itself.

---

## Delivery Notes

- The three-step explanation (understand, generate, optimize) should feel like
  opening a machine and showing someone how it works — calm, clear, sequential
- "Three biological questions" is the structural pivot — use your hands or a visual
  if possible to show the three layers
- End on the phased implementation — show that this is planned, not just imagined
- Don't rush the technical parts — the reviewers are smart and want to see you
  understand what you're building at depth
