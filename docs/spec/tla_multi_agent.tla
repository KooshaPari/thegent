--------------------------- MODULE thegent_multi_agent ---------------------------
EXTENDS Integers, Sequences, FiniteSets

(*
  WP-18001: TLA+ Specification for Multi-Agent Orchestration.
  Model safety properties: 
  - No two agents can hold an exclusive lock on the same resource.
  - All tasks must eventually reach a terminal state (Success/Failure).
*)

CONSTANTS Agents, Tasks, MaxDepth

VARIABLES 
    task_status,    \* TaskID -> {"pending", "running", "completed", "failed"}
    agent_locks,    \* AgentID -> Set of TaskIDs
    fork_depth      \* TaskID -> 0..MaxDepth

Vars == <<task_status, agent_locks, fork_depth>>

TypeOK == 
    /\ task_status \in [Tasks -> {"pending", "running", "completed", "failed"}]
    /\ agent_locks \in [Agents -> SUBSET Tasks]
    /\ fork_depth \in [Tasks -> 0..MaxDepth]

Init == 
    /\ task_status = [t \in Tasks |-> "pending"]
    /\ agent_locks = [a \in Agents |-> {}]
    /\ fork_depth = [t \in Tasks |-> 0]

(***************************************************************************)
(* Actions                                                                 *)
(***************************************************************************)

StartTask(a, t) ==
    /\ task_status[t] = "pending"
    /\ agent_locks[a] = {}
    /\ task_status' = [task_status EXCEPT ![t] = "running"]
    /\ agent_locks' = [agent_locks EXCEPT ![a] = {t}]
    /\ UNCHANGED <<fork_depth>>

CompleteTask(a, t) ==
    /\ task_status[t] = "running"
    /\ t \in agent_locks[a]
    /\ task_status' = [task_status EXCEPT ![t] = "completed"]
    /\ agent_locks' = [agent_locks EXCEPT ![a] = {}]
    /\ UNCHANGED <<fork_depth>>

FailTask(a, t) ==
    /\ task_status[t] = "running"
    /\ t \in agent_locks[a]
    /\ task_status' = [task_status EXCEPT ![t] = "failed"]
    /\ agent_locks' = [agent_locks EXCEPT ![a] = {}]
    /\ UNCHANGED <<fork_depth>>

ForkTask(a, t, t_child) ==
    /\ task_status[t] = "running"
    /\ t \in agent_locks[a]
    /\ task_status[t_child] = "pending"
    /\ fork_depth[t] < MaxDepth
    /\ fork_depth' = [fork_depth EXCEPT ![t_child] = fork_depth[t] + 1]
    /\ UNCHANGED <<task_status, agent_locks>>

(***************************************************************************)
(* Properties                                                              *)
(***************************************************************************)

(* Safety: No two agents hold the same task lock *)
MutualExclusion == 
    \forall a1, a2 \in Agents : a1 /= a2 => agent_locks[a1] \cap agent_locks[a2] = {}

(* Safety: Fork depth never exceeds MaxDepth *)
DepthLimit == \forall t \in Tasks : fork_depth[t] <= MaxDepth

Spec == Init /\ [][Next]_Vars

=============================================================================
