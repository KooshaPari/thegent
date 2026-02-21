from thegent.routing.litellm_router import EnhancedRouter


def test_router_metadata_model_preference():
    router = EnhancedRouter()

    # Normal routing
    route = router.route("Normal task", model="gpt-4")
    assert route.model == "gpt-4"

    # Routing from metadata
    metadata = {"model": "claude-3-opus"}
    route = router.route("Task from queue", queue_metadata=metadata)
    assert route.model == "claude-3-opus"

    # Routing from preferred_model
    metadata = {"preferred_model": "gemini-pro"}
    route = router.route("Task from queue", queue_metadata=metadata)
    assert route.model == "gemini-pro"

    # Explicit model overrides metadata
    metadata = {"model": "claude-3-opus"}
    route = router.route("Task from queue", model="gpt-4", queue_metadata=metadata)
    assert route.model == "gpt-4"
