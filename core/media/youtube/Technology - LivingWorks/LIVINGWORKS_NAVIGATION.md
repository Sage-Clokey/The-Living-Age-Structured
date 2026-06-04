# LivingWorks Navigation Design
## Why Genome Browsers Are Hard to Use — and How to Fix It

> "Navigate by relationship, not position. Navigate by question, not coordinate."

---

## The Problem With Genome Browsers

Genome browsers are the closest thing biology has to a LivingWorks interface.
They failed to become intuitive because of one original wrong choice:

**They are organized around the genome's coordinate system — not around human understanding.**

To go anywhere you need: `chr6:31,000,000-32,000,000`

That is not a place. It is an address in a coordinate system that means nothing until you already know what you are looking for. Everything else about the browser's difficulty flows from this.

### The Cascade of Problems

**You must know before you can find.**
There is no way to wander, discover, or follow a thread of curiosity.
You arrive knowing your destination. You leave having confirmed what you expected.
No browser has ever surprised its user with something they didn't already suspect.
That is not how living systems work. That is not how discovery works.

**Scale jumps are disorienting.**
Zooming from whole genome to a single gene to individual base pairs feels like teleportation — not travel. You lose your place. You lose the context. You forget why you came.
A living system has continuous scale. You should be able to move through it continuously.

**Data is separated from meaning.**
Peaks and bars and colored tracks require a learned visual language.
Nothing in the interface tells you what you are looking at or why it matters.
The system assumes expertise rather than building it.

**Everything is a snapshot.**
The genome is always in process — switching genes on and off, responding to signals, changing through developmental time. The browser shows you one frozen slice.
A living system in a static frame is no longer quite alive.

**The phenotype is invisible.**
You see sequence. You see expression levels. You never see what the organism does or becomes.
Cause is completely separated from effect.
The most important question — what does this produce in the world — is unanswerable from inside the browser.

**Relationships are hidden.**
The genome's most important feature is that everything regulates everything else in a network.
This is invisible in a browser. You see positions on a line.
The network — the actual intelligence of the genome — does not appear.

---

## The Root Cause

The genome browser was built by people who think of the genome as a **linear sequence of parts to be catalogued.**

It is actually a **living network to be understood.**

The interface reflects the machine model.
A living interface would reflect the network model.

---

## The Navigation Philosophy That Works

### 1. Start With the Organism. Drill Down to the Genome.

Current browsers do it backwards.
You start with the sequence and try to infer the biology.

The right direction: start with the biology, descend to the code.

*I want to understand how this cell decides to become a neuron.*
Show me the neuron.
Now show me what's active in it.
Now show me what regulates what's active.
Now show me the sequence of those regulators.

Every step in this journey has meaning. You never lose the thread of why you came.

### 2. Navigate by Question, Not Coordinate.

Not: `chr17:43,044,294-43,125,483`
But: *show me where breast cancer risk is encoded.*

Arrive with context already loaded — what you are looking at, why it matters, what is known about it, what is still unknown. Natural language as the primary navigation. Coordinates as the underlying address system the user never needs to see.

### 3. Navigate by Relationship, Not Position.

The genome is a network. Show it as a network first.

**Gene regulatory network as the primary view:**
- Nodes are genes
- Edges are regulatory relationships
- Edge thickness is relationship strength
- Color is activation state
- Pulsing is dynamic — the network breathes

Sequence is a zoom-in detail within a node.
**The network is the map. The sequence is the street-level view.**

When you want to know what controls a gene — follow the edges inward.
When you want to know what a gene affects — follow the edges outward.
Navigation is relational. You move through the logic of life, not through coordinates.

### 4. Continuous Zooming With Context at Every Scale.

```
Organism
  → Tissue
    → Cell type
      → Pathway
        → Gene
          → Regulatory region
            → Sequence
```

Each level of zoom reveals the next level of detail — but always in context of the level above. You never lose your place. You always know where you are in the larger pattern.

Like zooming into a map that keeps showing you the country outline even as the streets come into focus.

### 5. Time as a Navigation Dimension.

Not just *where* in the genome — but *when* in the life of the cell.

Move through developmental time and watch the network change. Watch a stem cell become a neuron — not as abstract data but as a changing pattern of activation visible in the network. The browser becomes a time machine through biological development.

Dimensions of time available:
- Developmental time (embryo → adult)
- Response time (before signal → after signal)
- Evolutionary time (compare species)
- Circadian time (morning → night → morning)
- Disease progression time (healthy → stressed → diseased → recovered)

### 6. The System Narrates.

As you explore, the system tells you what you're looking at.

Not a tooltip with coordinates — a running narration at whatever depth you want.

*This enhancer is active in neural tissue but silent in liver cells. When mutated in this population, individuals show this phenotype. Three other genes regulate its activity — here they are.*

The browser becomes a guide, not just a viewer.
The user builds understanding as they explore, not just before they start.

---

## The Five Navigation Elements (Genome Browser Redesigned)

### 1. The Organism View — Where You Start

A visual representation of the organism or system at its highest level.
Click on a tissue, a cell type, a phenotype of interest.
The system takes you inward — to the molecular activity underlying what you clicked.

You always start with the visible, lived biology.
You descend into the code from there.

### 2. The Network Map — The Primary Workspace

The gene regulatory network as a navigable landscape.
Not a diagram — a living map that updates as you move through time,
as you change conditions, as you compare states.

Navigate by following relationships.
Zoom in on any node to see its sequence, its variants, its expression history.
Zoom out to see its position in the full network.

**The network is always visible.** Even at maximum zoom on a single base pair, a minimap in the corner shows where you are in the network. You never lose context.

### 3. The Question Bar — Primary Navigation

A natural language input at the top of every view.

*Where is insulin regulated?*
*What changes between a healthy cell and this cancer cell?*
*Show me what's different between these two individuals.*
*What does this gene do?*

The system answers by taking you there — navigating the network to the relevant region, loading context, showing you the relationships that matter for your question.

Questions can be refined. *Now show me just the activators. Now compare to embryonic tissue. Now show me the evolutionary conservation.*

### 4. The Time Bar — Always Present

A timeline running along the bottom of every view.

The current moment is highlighted. Drag left or right and watch the network change. Watch expression levels rise and fall. Watch regulatory relationships strengthen and weaken. Watch the cell move through its developmental program.

Time is never hidden. It is always available. Because living systems are always in time.

### 5. The Phenotype Panel — Always Connected

A sidebar that always shows: *what does this produce?*

When you are looking at a gene — the panel shows what phenotypes are associated with its variation. What does loss of function look like in an organism? What does overexpression produce?

The connection between genotype and phenotype is never broken.
You always know what the code you are reading actually does in the world.

---

## How This Becomes the LivingWorks Interface

The genome browser redesigned is not separate from LivingWorks. It IS the LivingWorks interface — applied to designed living systems rather than biological ones.

| Genome Browser | LivingWorks |
|---|---|
| Organism | Site / Community |
| Tissue / Cell type | District / Building / Space |
| Gene regulatory network | Condition relationship network |
| Gene expression data | Condition layer data (climate, soil, social, ecological) |
| Sequence | Material and structural detail |
| Phenotype | Actual built form and its performance over time |
| Developmental time | Design evolution through time (year 1 → year 100) |
| Comparative genomics | Comparing this site to similar sites in the phenotypic library |
| Natural language navigation | *Show me what wants to grow on a north-facing slope in this climate* |
| Network as primary view | Condition relationships as primary view — not a floor plan |

**The navigation philosophy is identical:**
- Start with the place as it lives, not its coordinates
- Navigate by question and relationship, not address
- Show the network first, the detail on zoom
- Keep time always present
- Always show what the underlying conditions produce in the world

---

## What This Means for Bioinformatics

The difficulty of the genome browser is not a minor UX problem.
It is a symptom of how bioinformatics thinks about life.

When you design a tool around coordinates, you are saying: *the important thing about this gene is where it is.*

When you design a tool around relationships, you are saying: *the important thing about this gene is what it does in the context of everything else.*

The first framing is the machine model.
The second framing is the living systems model.

Bioinformatics that truly accounts for the living nature of what it studies would build tools organized around relationship, time, question, and phenotype — not around sequence coordinates.

LivingWorks is that tool.
Built first for designed systems.
But the same interface, the same navigation philosophy, could become the next generation of genome browser — the one that makes biology legible to the people who need to understand it most.

---

## As a Video

**Bridge Episode 8 — Why Genome Browsers Are Hard to Use**
*(And What That Tells Us About How We Think About Life)*

The difficulty of the interface is the argument.
If you design a tool around the machine model of life — coordinates, snapshots, isolated parts — the tool will be hard to use because life doesn't work that way.
A tool built on the living model — relationships, time, questions, phenotype — would feel like navigating a landscape you already half-know.

That is the test of whether a tool is alive:
**Does it feel like the thing it is working with?**

---

## Source Quotes

> "When you do computational biology, you are forced into humility. You learn that you cannot design an entire living world top-down. You can only nudge, explore, and make local improvements — then observe what the system does in response."

> "Bioinformatics can become the microscope for this philosophy — not only seeing life's code, but seeing life's order."

> "The intelligence of the genome is distributed across the entire network. When researchers try to understand development by studying one gene in isolation — they consistently fail. The behavior is in the network, not in any node."

> "life is not a block you carve into shape; it is a spiral you cultivate."
