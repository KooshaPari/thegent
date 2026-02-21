// Auto-generated usage examples for coordination
// Source: generate-api-docs.py

import { TeamCoordinator, broadcast_message, call_vote, cast_vote, detect_idle, get_vote_result, handle_task_completed, wait_for_task } from "./coordination";

// Create a TeamCoordinator instance
const teamcoordinator = new TeamCoordinator("example_session_dir");
teamcoordinator.broadcast_message("example_team_id", "example_sender", "example_message");
teamcoordinator.call_vote("example_team_id", "example_caller", "example_subject", undefined as unknown as Array<string>);
teamcoordinator.cast_vote("example_team_id", "example_vote_id", "example_voter", "example_option");
teamcoordinator.detect_idle("example_stdout");
teamcoordinator.get_vote_result("example_team_id", "example_vote_id");
teamcoordinator.handle_task_completed("example_team_id", "example_task_id", "example_result");
teamcoordinator.wait_for_task("example_team_id", "example_task_id", 0);

// Call broadcast_message
broadcast_message(undefined as unknown as any, "example_team_id", "example_sender", "example_message");
// Call call_vote
call_vote(undefined as unknown as any, "example_team_id", "example_caller", "example_subject", undefined as unknown as Array<string>);
// Call cast_vote
cast_vote(undefined as unknown as any, "example_team_id", "example_vote_id", "example_voter", "example_option");
// Call detect_idle
detect_idle(undefined as unknown as any, "example_stdout");
// Call get_vote_result
get_vote_result(undefined as unknown as any, "example_team_id", "example_vote_id");
// Call handle_task_completed
handle_task_completed(undefined as unknown as any, "example_team_id", "example_task_id", "example_result");
// Call wait_for_task
wait_for_task(undefined as unknown as any, "example_team_id", "example_task_id", 0);
