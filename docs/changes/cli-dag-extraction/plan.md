# Plan: cli-dag-extraction

## Objective

Extract Thegent's CLI task dependency graph logic into a standalone, reusable module with a clean public API for DAG construction, topological ordering, and conditional execution.

## Approach

1. Survey the existing DAG representation in thegent CLI code to identify the core data model
2. Define a clean DAG interface: nodes, edges, topological sort, cycle detection, fan-out expansion
3. Extract the logic into a dedicated module with type hints and Pydantic validation
4. Write a compatibility shim that maintains the existing CLI contract while delegating to the new module
5. Validate by running the full CLI test suite against the extracted module with parity assertions
