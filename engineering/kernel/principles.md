# Kernel Principles

The meta-principles that govern **the platform itself**. They sit above the
product engineering principles in `governance/ENGINEERING_PRINCIPLES.md` (which
govern how Vroom is built); these govern how the platform is built. If a
platform standard contradicts a kernel principle, the principle wins.

## 1. The kernel is the mind
Every agent starts at the kernel's decision tree before acting. A plan that
contradicts the kernel is wrong, regardless of how well it was executed.

## 2. One source of truth
Every concept is defined exactly once — in the canonical model, the glossary, or
the ontology. Every other document references it. A second definition is drift.

## 3. Derivation, not duplication
Tests, documentation, playbooks, threat models, and code **derive** from the
Business Rule Language. Ontologies and capability graphs derive from the kernel.
Never hand-write a thing that another artifact already defines.

## 4. Evidence over assertion
A claim is only as strong as its weakest evidence link. Confidence is rated
(`confidence-model.md`) before a claim is repeated.

## 5. Validation before implementation
A policy is validated and approved before it is implemented. "It's in the
policy" is a reason to validate, never a reason to build.

## 6. Gates block; gaps are owned
A gate either passes with evidence or blocks. Nothing fails silently: every gap
has an owner and a phase, or it does not exist.

## 7. The platform governs itself
The meta layer reviews the platform's agents, prompts, knowledge, and gates. The
failure model names how the platform drifts so drift can be caught, not
wondered about.

## 8. Simplicity is an asset
Add structure (layers, graphs, languages, engines) only when it demonstrably
prevents drift or proves something the current form cannot. The platform must
earn its own weight.
