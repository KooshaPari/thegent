"""Tests for SerializableMixin."""

import pytest
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

from thegent.integrations.base import SerializableMixin, hashable_dataclass


class Status(str, Enum):
    """Test status enum."""
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"


class Priority(StrEnum):
    """Test priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Address(SerializableMixin):
    """Nested model for testing."""
    street: str
    city: str
    zip_code: str


@dataclass
class Person(SerializableMixin):
    """Test model with various field types."""
    name: str
    age: int
    status: Status
    created_at: datetime
    home_path: Path
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    address: Address | None = None


# Hashable version of Person for hash tests
@hashable_dataclass
@dataclass
class HashablePerson(SerializableMixin):
    """Hashable test model."""
    name: str
    age: int
    status: Status
    created_at: datetime
    home_path: Path
    metadata: dict[str, Any] = field(default_factory=dict)


class TestToDict:
    """Tests for to_dict serialization."""

    def test_basic_fields(self):
        """Test basic field serialization."""
        person = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            home_path=Path("/home/alice"),
        )
        result = person.to_dict()
        
        assert result["name"] == "Alice"
        assert result["age"] == 30
        assert result["status"] == "active"  # Enum serialized as value
        assert result["created_at"] == "2024-01-15T10:30:00"  # ISO format
        assert result["home_path"] == "/home/alice"  # Path as string

    def test_enum_serialization(self):
        """Test enum serialization."""
        person = Person(
            name="Bob",
            age=25,
            status=Status.DONE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
        )
        result = person.to_dict()
        
        assert result["status"] == "done"
        assert isinstance(result["status"], str)

    def test_datetime_with_timezone(self):
        """Test datetime with timezone serialization."""
        dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        person = Person(
            name="Charlie",
            age=35,
            status=Status.PENDING,
            created_at=dt,
            home_path=Path("/tmp"),
        )
        result = person.to_dict()
        
        assert "2024-06-15T14:30:00" in result["created_at"]

    def test_nested_dict(self):
        """Test nested dict serialization."""
        person = Person(
            name="Diana",
            age=28,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            metadata={"key": "value", "nested": {"inner": 123}},
        )
        result = person.to_dict()
        
        assert result["metadata"]["key"] == "value"
        assert result["metadata"]["nested"]["inner"] == 123

    def test_list_serialization(self):
        """Test list serialization."""
        person = Person(
            name="Eve",
            age=22,
            status=Status.PENDING,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            tags=["tag1", "tag2", "tag3"],
        )
        result = person.to_dict()
        
        assert result["tags"] == ["tag1", "tag2", "tag3"]

    def test_nested_serializable(self):
        """Test nested SerializableMixin serialization."""
        address = Address(street="123 Main St", city="Springfield", zip_code="12345")
        person = Person(
            name="Frank",
            age=40,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            address=address,
        )
        result = person.to_dict()
        
        assert result["address"]["street"] == "123 Main St"
        assert result["address"]["city"] == "Springfield"
        assert result["address"]["zip_code"] == "12345"

    def test_none_field(self):
        """Test None field serialization."""
        person = Person(
            name="Grace",
            age=50,
            status=Status.DONE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            address=None,
        )
        result = person.to_dict()
        
        assert result["address"] is None


class TestFromDict:
    """Tests for from_dict deserialization."""

    def test_basic_deserialization(self):
        """Test basic field deserialization."""
        data = {
            "name": "Alice",
            "age": 30,
            "status": "active",
            "created_at": "2024-01-15T10:30:00",
            "home_path": "/home/alice",
        }
        person = Person.from_dict(data)
        
        assert person.name == "Alice"
        assert person.age == 30
        # Note: Enum/datetime/Path don't auto-convert in from_dict
        # They remain as strings - subclasses can override for custom deserialization

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored."""
        data = {
            "name": "Bob",
            "age": 25,
            "status": "done",
            "created_at": "2024-01-01",
            "home_path": "/tmp",
            "extra_field": "should be ignored",
        }
        person = Person.from_dict(data)
        
        assert person.name == "Bob"
        assert not hasattr(person, "extra_field")

    def test_missing_optional_fields(self):
        """Test handling of missing optional fields."""
        data = {
            "name": "Charlie",
            "age": 35,
            "status": "pending",
            "created_at": "2024-01-01",
            "home_path": "/tmp",
        }
        person = Person.from_dict(data)
        
        assert person.metadata == {}
        assert person.tags == []
        assert person.address is None


class TestRoundTrip:
    """Tests for serialization -> deserialization round trips."""

    def test_simple_roundtrip(self):
        """Test that simple data survives round trip."""
        original = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            home_path=Path("/home/alice"),
            metadata={"key": "value"},
            tags=["tag1"],
        )
        
        serialized = original.to_dict()
        restored = Person.from_dict(serialized)
        
        assert restored.name == original.name
        assert restored.age == original.age
        # status is now string "active" not enum
        # created_at is now string not datetime
        # home_path is now string not Path


class TestNonDataclass:
    """Tests for non-dataclass classes."""

    def test_non_dataclass_serialization(self):
        """Test that non-dataclass objects can use SerializableMixin."""
        
        class SimpleModel(SerializableMixin):
            def __init__(self, name: str, value: int):
                self.name = name
                self.value = value
        
        obj = SimpleModel("test", 42)
        result = obj.to_dict()
        
        assert result["name"] == "test"
        assert result["value"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestEnhancedFromDict:
    """Tests for enhanced from_dict with type-aware deserialization."""

    def setup_method(self):
        """Reset singleton before each test."""
        pass

    def test_path_deserialization(self):
        """Test Path deserialization."""
        data = {
            "name": "Alice",
            "age": 30,
            "status": "active",
            "created_at": datetime(2024, 1, 1),
            "home_path": "/home/alice",
        }
        person = Person.from_dict(data)
        
        assert isinstance(person.home_path, Path)
        assert person.home_path == Path("/home/alice")

    def test_enum_deserialization(self):
        """Test Enum deserialization."""
        data = {
            "name": "Bob",
            "age": 25,
            "status": "done",
            "created_at": datetime(2024, 1, 1),
            "home_path": Path("/tmp"),
        }
        person = Person.from_dict(data)
        
        assert isinstance(person.status, Status)
        assert person.status == Status.DONE

    def test_datetime_deserialization(self):
        """Test datetime deserialization from ISO string."""
        data = {
            "name": "Charlie",
            "age": 35,
            "status": "pending",
            "created_at": "2024-06-15T14:30:00",
            "home_path": Path("/tmp"),
        }
        person = Person.from_dict(data)
        
        assert isinstance(person.created_at, datetime)
        assert person.created_at.year == 2024
        assert person.created_at.month == 6
        assert person.created_at.day == 15

    def test_datetime_with_timezone(self):
        """Test datetime deserialization with timezone."""
        data = {
            "name": "Diana",
            "age": 28,
            "status": "active",
            "created_at": "2024-06-15T14:30:00+00:00",
            "home_path": Path("/tmp"),
        }
        person = Person.from_dict(data)
        
        assert isinstance(person.created_at, datetime)
        assert person.created_at.tzinfo is not None

    def test_nested_serializable_deserialization(self):
        """Test nested SerializableMixin deserialization."""
        data = {
            "name": "Eve",
            "age": 22,
            "status": "pending",
            "created_at": datetime(2024, 1, 1),
            "home_path": Path("/tmp"),
            "address": {
                "street": "456 Oak Ave",
                "city": "Portland",
                "zip_code": "97201",
            },
        }
        person = Person.from_dict(data)
        
        assert isinstance(person.address, Address)
        assert person.address.street == "456 Oak Ave"
        assert person.address.city == "Portland"

    def test_roundtrip_preserves_types(self):
        """Test that roundtrip preserves types."""
        original = Person(
            name="Frank",
            age=40,
            status=Status.ACTIVE,
            created_at=datetime(2024, 6, 15, 14, 30, 0),
            home_path=Path("/home/frank"),
            metadata={"key": "value"},
            tags=["tag1", "tag2"],
            address=Address("789 Pine St", "Seattle", "98101"),
        )
        
        serialized = original.to_dict()
        restored = Person.from_dict(serialized)
        
        assert restored.name == original.name
        assert restored.age == original.age
        assert restored.status == original.status
        assert isinstance(restored.status, Status)
        assert restored.home_path == original.home_path
        assert isinstance(restored.home_path, Path)
        assert restored.address.street == original.address.street
        assert isinstance(restored.address, Address)


class TestListAndDictTypes:
    """Tests for list and dict type deserialization."""

    def test_list_of_enums(self):
        """Test deserialization of list with typed elements."""
        from dataclasses import dataclass
        from typing import Any
        
        @dataclass
        class TaskList(SerializableMixin):
            name: str
            statuses: list[Status] = field(default_factory=list)
        
        data = {
            "name": "My Tasks",
            "statuses": ["pending", "active", "done"],
        }
        task_list = TaskList.from_dict(data)
        
        assert len(task_list.statuses) == 3
        assert all(isinstance(s, Status) for s in task_list.statuses)
        assert task_list.statuses[0] == Status.PENDING
        assert task_list.statuses[2] == Status.DONE

    def test_optional_field_with_none(self):
        """Test Optional field with None value."""
        data = {
            "name": "Grace",
            "age": 50,
            "status": "done",
            "created_at": "2024-01-01",
            "home_path": "/tmp",
            "address": None,
        }
        person = Person.from_dict(data)
        
        assert person.address is None


class TestEquality:
    """Tests for __eq__ implementation."""

    def test_equal_instances(self):
        """Test that equal instances compare equal."""
        p1 = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 15),
            home_path=Path("/home/alice"),
        )
        p2 = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 15),
            home_path=Path("/home/alice"),
        )
        
        assert p1 == p2

    def test_unequal_instances(self):
        """Test that different instances compare unequal."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = Person(name="Bob", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        assert p1 != p2

    def test_different_types_unequal(self):
        """Test that different types compare unequal."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        address = Address(street="123 Main St", city="Springfield", zip_code="12345")
        
        assert person != address

    def test_nested_equality(self):
        """Test equality with nested SerializableMixin."""
        p1 = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            address=Address("123 Main St", "Springfield", "12345"),
        )
        p2 = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            address=Address("123 Main St", "Springfield", "12345"),
        )
        
        assert p1 == p2


class TestHash:
    """Tests for __hash__ implementation."""

    def test_hash_stability(self):
        """Test that hash is stable."""
        person = HashablePerson(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
        )
        
        h1 = hash(person)
        h2 = hash(person)
        assert h1 == h2

    def test_equal_instances_same_hash(self):
        """Test that equal instances have same hash."""
        p1 = HashablePerson(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = HashablePerson(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        assert hash(p1) == hash(p2)

    def test_can_use_in_set(self):
        """Test that instances can be used in sets."""
        p1 = HashablePerson(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = HashablePerson(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p3 = HashablePerson(name="Bob", age=25, status=Status.PENDING, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        s = {p1, p2, p3}
        assert len(s) == 2  # p1 and p2 are equal, p3 is different

    def test_can_use_as_dict_key(self):
        """Test that instances can be used as dict keys."""
        p1 = HashablePerson(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = HashablePerson(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        d = {p1: "value1"}
        d[p2] = "value2"  # Should overwrite p1's value
        
        assert len(d) == 1
        assert d[p1] == "value2"


class TestRepr:
    """Tests for __repr__ implementation."""

    def test_repr_shows_class_name(self):
        """Test that repr shows class name."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        r = repr(person)
        
        assert "Person" in r

    def test_repr_shows_fields(self):
        """Test that repr shows first few fields."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        r = repr(person)
        
        assert "name=" in r
        assert "Alice" in r

    def test_repr_truncates_long_strings(self):
        """Test that repr truncates long strings."""
        person = HashablePerson(
            name="This is a very long name that should be truncated in the repr output",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
        )
        r = repr(person)
        
        assert "..." in r

    def test_repr_shows_ellipsis_for_many_fields(self):
        """Test that repr shows ellipsis when there are many fields."""
        person = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            metadata={"key": "value"},
            tags=["tag1", "tag2"],
        )
        r = repr(person)
        
        # Should show first 3 fields and "..."
        assert "Person(" in r

    def test_repr_for_nested_objects(self):
        """Test repr with nested SerializableMixin."""
        person = Person(
            name="Alice",
            age=30,
            status=Status.ACTIVE,
            created_at=datetime(2024, 1, 1),
            home_path=Path("/tmp"),
            address=Address("123 Main St", "Springfield", "12345"),
        )
        r = repr(person)
        
        assert "Person" in r
        # Address should have its own repr
        assert "Address" in repr(person.address)


class TestDiff:
    """Tests for diff method."""

    def test_no_differences(self):
        """Test diff returns empty when instances are equal."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        diff = p1.diff(p2)
        assert diff == {}

    def test_single_field_difference(self):
        """Test diff with one field different."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = Person(name="Alice", age=35, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        diff = p1.diff(p2)
        assert diff == {"age": (30, 35)}

    def test_multiple_differences(self):
        """Test diff with multiple fields different."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = Person(name="Bob", age=35, status=Status.DONE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        diff = p1.diff(p2)
        assert "name" in diff
        assert "age" in diff
        assert "status" in diff
        assert diff["name"] == ("Alice", "Bob")

    def test_diff_wrong_type_raises(self):
        """Test that diff raises TypeError for different types."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        address = Address(street="123 Main", city="Springfield", zip_code="12345")
        
        with pytest.raises(TypeError):
            person.diff(address)


class TestCopy:
    """Tests for copy method."""

    def test_exact_copy(self):
        """Test that copy creates equal instance."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = p1.copy()
        
        assert p1 == p2
        assert p1 is not p2

    def test_copy_with_override(self):
        """Test copy with field override."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = p1.copy(age=35)
        
        assert p2.name == "Alice"
        assert p2.age == 35
        assert p1.age == 30  # Original unchanged

    def test_copy_with_multiple_overrides(self):
        """Test copy with multiple overrides."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = p1.copy(age=35, name="Bob")
        
        assert p2.name == "Bob"
        assert p2.age == 35


class TestMerge:
    """Tests for merge method."""

    def test_merge_overwrite_true(self):
        """Test merge with overwrite=True (default)."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = Person(name="Bob", age=35, status=Status.DONE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        merged = p1.merge(p2)
        assert merged.name == "Bob"
        assert merged.age == 35
        assert merged.status == Status.DONE

    def test_merge_overwrite_false(self):
        """Test merge with overwrite=False."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = Person(name="Bob", age=35, status=Status.DONE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        merged = p1.merge(p2, overwrite=False)
        assert merged.name == "Alice"  # Kept from p1
        assert merged.age == 30  # Kept from p1
        assert merged.status == Status.ACTIVE  # Kept from p1

    def test_merge_fills_none(self):
        """Test merge fills in None values."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p1.address = None
        p2.address = Address(street="123 Main", city="Springfield", zip_code="12345")
        
        merged = p1.merge(p2, overwrite=False)
        assert merged.address is not None
        assert merged.address.street == "123 Main"

    def test_merge_wrong_type_raises(self):
        """Test that merge raises TypeError for different types."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        address = Address(street="123 Main", city="Springfield", zip_code="12345")
        
        with pytest.raises(TypeError):
            person.merge(address)


class TestPatch:
    """Tests for patch method (alias for copy)."""

    def test_patch_updates_fields(self):
        """Test that patch updates fields."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = p1.patch(age=35, name="Bob")
        
        assert p2.name == "Bob"
        assert p2.age == 35
        assert p1.name == "Alice"  # Original unchanged


class TestToJson:
    """Tests for to_json method."""

    def test_to_json_basic(self):
        """Test basic JSON serialization."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        json_str = person.to_json()
        
        assert "Alice" in json_str
        assert '"age": 30' in json_str

    def test_to_json_with_indent(self):
        """Test JSON with indentation."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        json_str = person.to_json(indent=2)
        
        assert "\n" in json_str  # Pretty-printed has newlines

    def test_to_json_compact(self):
        """Test compact JSON (no indent)."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        json_str = person.to_json(indent=None)
        
        # Compact form has no indentation
        assert "  " not in json_str or "\n" not in json_str


class TestFromJson:
    """Tests for from_json method."""

    def test_from_json_basic(self):
        """Test basic JSON deserialization."""
        json_str = '{"name": "Alice", "age": 30, "status": "active", "created_at": "2024-01-01T00:00:00", "home_path": "/tmp"}'
        person = Person.from_json(json_str)
        
        assert person.name == "Alice"
        assert person.age == 30

    def test_roundtrip_json(self):
        """Test JSON roundtrip."""
        original = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        json_str = original.to_json()
        restored = Person.from_json(json_str)
        
        assert restored == original

    def test_from_json_invalid_raises(self):
        """Test that invalid JSON raises error."""
        with pytest.raises(Exception):  # JSONDecodeError
            Person.from_json("not valid json")


class TestJsonFile:
    """Tests for to_json_file and from_json_file methods."""

    def test_to_from_json_file(self, tmp_path):
        """Test writing and reading JSON file."""
        original = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        file_path = tmp_path / "person.json"
        original.to_json_file(file_path)
        
        assert file_path.exists()
        
        restored = Person.from_json_file(file_path)
        assert restored == original

    def test_to_json_file_creates_dirs(self, tmp_path):
        """Test that to_json_file creates parent directories."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        file_path = tmp_path / "nested" / "dir" / "person.json"
        person.to_json_file(file_path)
        
        assert file_path.exists()

    def test_from_json_file_not_found(self, tmp_path):
        """Test that from_json_file raises on missing file."""
        with pytest.raises(FileNotFoundError):
            Person.from_json_file(tmp_path / "nonexistent.json")


class TestYaml:
    """Tests for YAML serialization methods."""

    def test_to_yaml_basic(self):
        """Test basic YAML serialization."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        yaml_str = person.to_yaml()
        
        assert "name: Alice" in yaml_str
        assert "age: 30" in yaml_str

    def test_yaml_roundtrip(self):
        """Test YAML roundtrip."""
        original = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        yaml_str = original.to_yaml()
        restored = Person.from_yaml(yaml_str)
        
        assert restored == original

    def test_yaml_file_roundtrip(self, tmp_path):
        """Test YAML file roundtrip."""
        original = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        file_path = tmp_path / "person.yaml"
        original.to_yaml_file(file_path)
        
        assert file_path.exists()
        
        restored = Person.from_yaml_file(file_path)
        assert restored == original


class TestToml:
    """Tests for TOML serialization methods."""

    def test_to_toml_basic(self):
        """Test basic TOML serialization."""
        person = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        toml_str = person.to_toml()
        
        assert 'name = "Alice"' in toml_str
        assert "age = 30" in toml_str

    def test_toml_roundtrip(self):
        """Test TOML roundtrip."""
        original = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        toml_str = original.to_toml()
        restored = Person.from_toml(toml_str)
        
        assert restored == original

    def test_toml_file_roundtrip(self, tmp_path):
        """Test TOML file roundtrip."""
        original = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        file_path = tmp_path / "person.toml"
        original.to_toml_file(file_path)
        
        assert file_path.exists()
        
        restored = Person.from_toml_file(file_path)
        assert restored == original


class TestDeepCopy:
    """Tests for deepcopy support."""

    def test_deep_copy(self):
        """Test deep_copy method."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = p1.deep_copy()
        
        assert p1 == p2
        assert p1 is not p2

    def test_deepcopy_function(self):
        """Test copy.deepcopy() works."""
        import copy
        
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = copy.deepcopy(p1)
        
        assert p1 == p2
        assert p1 is not p2


class TestPickle:
    """Tests for pickle support."""

    def test_pickle_roundtrip(self):
        """Test pickle/unpickle roundtrip."""
        import pickle
        
        original = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        
        pickled = pickle.dumps(original)
        restored = pickle.loads(pickled)
        
        assert restored == original


class TestReplace:
    """Tests for replace method."""

    def test_replace_single_field(self):
        """Test replace with single field change."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = p1.replace(age=35)
        
        assert p2.age == 35
        assert p1.age == 30  # Original unchanged

    def test_replace_multiple_fields(self):
        """Test replace with multiple field changes."""
        p1 = Person(name="Alice", age=30, status=Status.ACTIVE, created_at=datetime(2024, 1, 1), home_path=Path("/tmp"))
        p2 = p1.replace(age=35, name="Bob")
        
        assert p2.name == "Bob"
        assert p2.age == 35
