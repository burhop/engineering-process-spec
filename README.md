# Engineering Process Specification

An experimental, implementation-neutral specification for sharing engineering
processes between human or AI creators and process executors.

## Status

Early draft. No stable language, compatibility guarantee, or standards-body
endorsement is claimed. The project name is provisional.

## Scope

Describe process inputs, operations, dependencies, required capabilities,
outputs, and acceptance criteria so independent systems can exchange and
execute a process with the same intended meaning.

## Relationship to Wright

[Wright](https://github.com/burhop/wright) is the initial implementation and
experimentation environment. Its versioned implementation contracts define
current behavior while the language is evolving.

This repository will distinguish proposals from implemented behavior and link
to exact Wright revisions. Once a portable subset is agreed and independently
implemented, its specification can become authoritative for that subset.

## First milestone

Exchange a process authored in Wright with a separate executor, retaining its
inputs, required capabilities, expected outputs, and acceptance criteria.

Start with a quantity calculation, a CAD modification with measurable checks,
and a process requiring human approval. Examples and language definitions will
be added as their semantics become clear.

## Working process

Use issues for questions and proposals, and pull requests for specification
changes. Keep implementation code in Wright for now. Licensing and external
contribution terms will be decided before inviting outside adoption.
