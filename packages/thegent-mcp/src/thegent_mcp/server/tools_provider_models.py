"""Provider/model management tool registrations for MCP server."""

from __future__ import annotations

from fastmcp import FastMCP


def register_provider_model_tools(
    *, mcp: FastMCP
) -> tuple[
    object,
    object,
    object,
    object,
    object,
    object,
    object,
    object,
    object,
    object,
    object,
    object,
    object,
]:
    @mcp.tool()
    def list_providers(include_credentials: bool = False) -> str:
        """List all configured providers with their settings."""
        import json

        from thegent.provider_model_manager import list_providers as _list_providers

        return json.dumps(_list_providers(include_credentials=include_credentials).decode().decode(), indent=2)

    @mcp.tool()
    def get_provider(name: str) -> str:
        """Get a specific provider configuration."""
        import json

        from thegent.provider_model_manager import get_provider as _get_provider

        result = _get_provider(name)
        if result is None:
            return json.dumps({"error": f"Provider '{name}' not found"}).decode().decode()
        return json.dumps(result, indent=2).decode().decode()

    @mcp.tool()
    def add_provider(
        name: str,
        base_url: str,
        model: str,
        api_key: str | None = None,
        extra_aliases: list[str] | None = None,
        login_url: str | None = None,
    ) -> str:
        """Add a new provider configuration."""
        import json

        from thegent.provider_model_manager import add_provider as _add_provider

        success, msg = _add_provider(
            name=name,
            base_url=base_url,
            model=model,
            api_key=api_key,
            extra_aliases=extra_aliases,
            login_url=login_url,
        )
        return json.dumps({"success": success, "message": msg}).decode().decode()

    @mcp.tool()
    def update_provider(
        name: str,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        extra_aliases: list[str] | None = None,
    ) -> str:
        """Update an existing provider configuration."""
        import json

        from thegent.provider_model_manager import update_provider as _update_provider

        success, msg = _update_provider(
            name=name,
            base_url=base_url,
            model=model,
            api_key=api_key,
            extra_aliases=extra_aliases,
        )
        return json.dumps({"success": success, "message": msg}).decode().decode()

    @mcp.tool()
    def delete_provider(name: str, remove_credentials: bool = True) -> str:
        """Delete a provider configuration."""
        import json

        from thegent.provider_model_manager import delete_provider as _delete_provider

        success, msg = _delete_provider(name, remove_credentials=remove_credentials)
        return json.dumps({"success": success, "message": msg}).decode().decode()

    @mcp.tool()
    def list_credentials() -> str:
        """List all configured credentials (API keys and OAuth)."""
        import json

        from thegent.provider_model_manager import list_credentials as _list_credentials

        return json.dumps(_list_credentials().decode().decode(), indent=2)

    @mcp.tool()
    def add_api_key(provider: str, api_key: str) -> str:
        """Add or update API key for a provider."""
        import json

        from thegent.provider_model_manager import add_api_key as _add_api_key

        success, msg = _add_api_key(provider, api_key)
        return json.dumps({"success": success, "message": msg}).decode().decode()

    @mcp.tool()
    def remove_api_key(provider: str) -> str:
        """Remove API key for a provider."""
        import json

        from thegent.provider_model_manager import remove_api_key as _remove_api_key

        success, msg = _remove_api_key(provider)
        return json.dumps({"success": success, "message": msg}).decode().decode()

    @mcp.tool()
    def validate_provider(name: str) -> str:
        """Validate a provider by testing connectivity and credentials."""
        import json

        from thegent.provider_model_manager import validate_provider as _validate_provider

        success, msg, details = _validate_provider(name)
        return json.dumps(
            {
                "success": success,
                "message": msg,
                "details": details,
            }
        )

    @mcp.tool()
    def discover_models(provider: str | None = None) -> str:
        """Discover available models from provider APIs."""
        import json

        from thegent.provider_model_manager import discover_models as _discover_models

        return json.dumps(_discover_models(provider).decode().decode(), indent=2)

    @mcp.tool()
    def list_models(provider: str | None = None) -> str:
        """List all models, optionally filtered by provider."""
        import json

        from thegent.provider_model_manager import list_models as _list_models

        return json.dumps(_list_models(provider).decode().decode(), indent=2)

    @mcp.tool()
    def add_model_alias(provider: str, model: str, alias: str) -> str:
        """Add a model alias for a provider."""
        import json

        from thegent.provider_model_manager import add_model_alias as _add_model_alias

        success, msg = _add_model_alias(provider, model, alias)
        return json.dumps({"success": success, "message": msg}).decode().decode()

    @mcp.tool()
    def remove_model_alias(provider: str, alias: str) -> str:
        """Remove a model alias from a provider."""
        import json

        from thegent.provider_model_manager import remove_model_alias as _remove_model_alias

        success, msg = _remove_model_alias(provider, alias)
        return json.dumps({"success": success, "message": msg}).decode().decode()

    return (
        list_providers,
        get_provider,
        add_provider,
        update_provider,
        delete_provider,
        list_credentials,
        add_api_key,
        remove_api_key,
        validate_provider,
        discover_models,
        list_models,
        add_model_alias,
        remove_model_alias,
    )
