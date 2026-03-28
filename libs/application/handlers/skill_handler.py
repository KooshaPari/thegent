"""
Skill Command and Query Handlers

Handlers implement the application layer logic by:
1. Receiving commands/queries from inbound ports
2. Orchestrating domain logic
3. Using outbound ports for persistence and events

Following CQRS and hexagonal architecture patterns.
"""

from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

from ...ports.inbound import (
    CommandHandler,
    QueryHandler,
    CommandResult,
    QueryResult,
)
from ...ports.outbound import Repository, EventBus, Cache
from ...domain.entities.skill import (
    Skill,
    SkillId,
    SkillCategory,
    SkillCreated,
)
from ...application.commands.skill_commands import (
    CreateSkillCommand,
    UpdateSkillCommand,
    DeleteSkillCommand,
    ActivateSkillCommand,
    DeactivateSkillCommand,
    AddToolToSkillCommand,
    RemoveToolFromSkillCommand,
    CloneSkillCommand,
)
from ...application.queries import (
    GetSkillQuery,
    ListSkillsQuery,
    SearchSkillsQuery,
)
from ...domain.services import SkillValidator

if TYPE_CHECKING:
    from hexagonal.domain.entities.skill import DomainEvent


@dataclass
class SkillCommandHandler(CommandHandler[CreateSkillCommand]):
    """
    Handler for skill commands.

    Orchestrates the business logic for skill operations by:
    - Validating input
    - Creating/updating domain entities
    - Persisting via repository
    - Publishing domain events
    """

    skill_repository: Repository
    event_bus: Optional[EventBus] = None
    cache: Optional[Cache] = None

    async def handle(self, command) -> CommandResult:
        """Handle a skill command."""
        # Route to appropriate handler method
        handlers = {
            CreateSkillCommand: self._handle_create,
            UpdateSkillCommand: self._handle_update,
            DeleteSkillCommand: self._handle_delete,
            ActivateSkillCommand: self._handle_activate,
            DeactivateSkillCommand: self._handle_deactivate,
            AddToolToSkillCommand: self._handle_add_tool,
            RemoveToolFromSkillCommand: self._handle_remove_tool,
            CloneSkillCommand: self._handle_clone,
        }

        handler = handlers.get(type(command))
        if not handler:
            return CommandResult.error(f"Unknown command type: {type(command)}")

        return await handler(command)

    async def _handle_create(self, command: CreateSkillCommand) -> CommandResult:
        """Handle create skill command."""
        try:
            # Validate command
            if not command.name.strip():
                return CommandResult.error("Skill name cannot be empty")
            if not command.instructions.strip():
                return CommandResult.error("Skill instructions cannot be empty")

            # Parse category
            try:
                category = SkillCategory(command.category.lower())
            except ValueError:
                return CommandResult.error(f"Invalid category: {command.category}")

            # Create domain entity
            skill = Skill(
                id=SkillId.generate(),
                name=command.name.strip(),
                description=command.description.strip(),
                category=category,
                instructions=command.instructions.strip(),
                tools=list(command.tools),
                tags=list(command.tags),
            )

            # Validate domain entity
            validator = SkillValidator()
            if not validator.is_valid(skill):
                return CommandResult.error(
                    f"Validation failed: {', '.join(validator.get_errors())}"
                )

            # Persist
            await self.skill_repository.save(skill)

            # Publish events
            if self.event_bus:
                events = skill.pull_and_merge_events()
                for event in events:
                    await self.event_bus.publish(event)

            # Invalidate cache
            if self.cache:
                await self.cache.delete(f"skill:{skill.id}")

            return CommandResult.ok(
                data={"skill_id": str(skill.id), "name": skill.name},
                command_id=command.command_id,
            )

        except Exception as e:
            return CommandResult.error(f"Failed to create skill: {str(e)}")

    async def _handle_update(self, command: UpdateSkillCommand) -> CommandResult:
        """Handle update skill command."""
        try:
            # Find existing skill
            skill = await self.skill_repository.find_by_id(command.skill_id)
            if not skill:
                return CommandResult.error(f"Skill not found: {command.skill_id}")

            # Update skill
            skill.update(
                name=command.name,
                description=command.description,
                instructions=command.instructions,
                tools=command.tools,
                tags=command.tags,
            )

            # Persist
            await self.skill_repository.save(skill)

            # Publish events
            if self.event_bus:
                events = skill.pull_and_merge_events()
                for event in events:
                    await self.event_bus.publish(event)

            # Invalidate cache
            if self.cache:
                await self.cache.delete(f"skill:{skill.id}")

            return CommandResult.ok(
                data={"skill_id": str(skill.id), "updated": True},
                command_id=command.command_id,
            )

        except ValueError as e:
            return CommandResult.error(f"Validation error: {str(e)}")
        except Exception as e:
            return CommandResult.error(f"Failed to update skill: {str(e)}")

    async def _handle_delete(self, command: DeleteSkillCommand) -> CommandResult:
        """Handle delete skill command."""
        try:
            # Check exists
            exists = await self.skill_repository.exists(command.skill_id)
            if not exists:
                return CommandResult.error(f"Skill not found: {command.skill_id}")

            # Delete
            await self.skill_repository.delete(command.skill_id)

            # Invalidate cache
            if self.cache:
                await self.cache.delete(f"skill:{command.skill_id}")

            return CommandResult.ok(
                data={"skill_id": command.skill_id, "deleted": True},
                command_id=command.command_id,
            )

        except Exception as e:
            return CommandResult.error(f"Failed to delete skill: {str(e)}")

    async def _handle_activate(self, command: ActivateSkillCommand) -> CommandResult:
        """Handle activate skill command."""
        try:
            skill = await self.skill_repository.find_by_id(command.skill_id)
            if not skill:
                return CommandResult.error(f"Skill not found: {command.skill_id}")

            skill.activate()
            await self.skill_repository.save(skill)

            if self.event_bus:
                for event in skill.pull_and_merge_events():
                    await self.event_bus.publish(event)

            return CommandResult.ok(
                data={"skill_id": str(skill.id), "is_active": True},
                command_id=command.command_id,
            )

        except Exception as e:
            return CommandResult.error(f"Failed to activate skill: {str(e)}")

    async def _handle_deactivate(self, command: DeactivateSkillCommand) -> CommandResult:
        """Handle deactivate skill command."""
        try:
            skill = await self.skill_repository.find_by_id(command.skill_id)
            if not skill:
                return CommandResult.error(f"Skill not found: {command.skill_id}")

            skill.deactivate()
            await self.skill_repository.save(skill)

            if self.event_bus:
                for event in skill.pull_and_merge_events():
                    await self.event_bus.publish(event)

            return CommandResult.ok(
                data={"skill_id": str(skill.id), "is_active": False},
                command_id=command.command_id,
            )

        except Exception as e:
            return CommandResult.error(f"Failed to deactivate skill: {str(e)}")

    async def _handle_add_tool(self, command: AddToolToSkillCommand) -> CommandResult:
        """Handle add tool command."""
        try:
            skill = await self.skill_repository.find_by_id(command.skill_id)
            if not skill:
                return CommandResult.error(f"Skill not found: {command.skill_id}")

            skill.add_tool(command.tool)
            await self.skill_repository.save(skill)

            if self.event_bus:
                for event in skill.pull_and_merge_events():
                    await self.event_bus.publish(event)

            return CommandResult.ok(
                data={"skill_id": str(skill.id), "tool_added": command.tool},
                command_id=command.command_id,
            )

        except Exception as e:
            return CommandResult.error(f"Failed to add tool: {str(e)}")

    async def _handle_remove_tool(self, command: RemoveToolFromSkillCommand) -> CommandResult:
        """Handle remove tool command."""
        try:
            skill = await self.skill_repository.find_by_id(command.skill_id)
            if not skill:
                return CommandResult.error(f"Skill not found: {command.skill_id}")

            skill.remove_tool(command.tool)
            await self.skill_repository.save(skill)

            if self.event_bus:
                for event in skill.pull_and_merge_events():
                    await self.event_bus.publish(event)

            return CommandResult.ok(
                data={"skill_id": str(skill.id), "tool_removed": command.tool},
                command_id=command.command_id,
            )

        except Exception as e:
            return CommandResult.error(f"Failed to remove tool: {str(e)}")

    async def _handle_clone(self, command: CloneSkillCommand) -> CommandResult:
        """Handle clone skill command."""
        # Implementation would fetch from source and create
        return CommandResult.error("Clone command not yet implemented")


class SkillQueryHandler(QueryHandler[GetSkillQuery]):
    """Handler for skill queries."""

    skill_repository: Repository
    cache: Optional[Cache] = None

    async def handle(self, query) -> QueryResult:
        """Handle a skill query."""
        handlers = {
            GetSkillQuery: self._handle_get,
            ListSkillsQuery: self._handle_list,
            SearchSkillsQuery: self._handle_search,
        }

        handler = handlers.get(type(query))
        if not handler:
            return QueryResult.error(f"Unknown query type: {type(query)}")

        return await handler(query)

    async def _handle_get(self, query: GetSkillQuery) -> QueryResult:
        """Handle get skill query."""
        try:
            # Check cache first
            if self.cache:
                cached = await self.cache.get(f"skill:{query.skill_id}")
                if cached:
                    return QueryResult.ok(data=cached, query_id=query.query_id)

            # Fetch from repository
            skill = await self.skill_repository.find_by_id(query.skill_id)
            if not skill:
                return QueryResult.error(f"Skill not found: {query.skill_id}")

            # Cache result
            if self.cache:
                await self.cache.set(f"skill:{query.skill_id}", skill)

            return QueryResult.ok(data=skill, query_id=query.query_id)

        except Exception as e:
            return QueryResult.error(f"Failed to get skill: {str(e)}")

    async def _handle_list(self, query: ListSkillsQuery) -> QueryResult:
        """Handle list skills query."""
        try:
            skills = await self.skill_repository.find_all(
                limit=query.limit, offset=query.offset
            )

            # Filter by category if specified
            if query.category:
                from hexagonal.domain.entities.skill import SkillCategory
                try:
                    cat = SkillCategory(query.category.lower())
                    skills = [s for s in skills if s.category == cat]
                except ValueError:
                    pass

            # Filter by tag if specified
            if query.tag:
                skills = [s for s in skills if query.tag in s.tags]

            # Filter by active status if specified
            if query.is_active is not None:
                skills = [s for s in skills if s.is_active == query.is_active]

            return QueryResult.ok(
                data=skills,
                query_id=query.query_id,
                total=len(skills),
            )

        except Exception as e:
            return QueryResult.error(f"Failed to list skills: {str(e)}")

    async def _handle_search(self, query: SearchSkillsQuery) -> QueryResult:
        """Handle search skills query."""
        try:
            skills = await self.skill_repository.find_all(limit=query.limit)

            # Filter by search term
            search_lower = query.search_term.lower()
            skills = [
                s
                for s in skills
                if search_lower in s.name.lower() or search_lower in s.description.lower()
            ]

            return QueryResult.ok(
                data=skills,
                query_id=query.query_id,
                total=len(skills),
            )

        except Exception as e:
            return QueryResult.error(f"Failed to search skills: {str(e)}")
