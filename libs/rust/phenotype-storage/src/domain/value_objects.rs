//! Value objects for storage operations.
//!
//! These are immutable types that are defined by their attributes
//! rather than their identity.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Pagination parameters for query operations.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct Pagination {
    /// Page number (0-indexed)
    pub page: usize,
    /// Page size
    pub page_size: usize,
}

impl Pagination {
    /// Create new pagination with page number and size.
    pub fn new(page: usize, page_size: usize) -> Self {
        Self { page, page_size }
    }

    /// Calculate offset for database queries.
    pub fn offset(&self) -> usize {
        self.page * self.page_size
    }

    /// Calculate total pages given total items.
    pub fn total_pages(&self, total_items: usize) -> usize {
        (total_items + self.page_size - 1) / self.page_size
    }
}

impl Default for Pagination {
    fn default() -> Self {
        Self {
            page: 0,
            page_size: 20,
        }
    }
}

/// Sort direction for queries.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum SortDirection {
    Ascending,
    Descending,
}

impl Default for SortDirection {
    fn default() -> Self {
        Self::Ascending
    }
}

/// Sort parameter for queries.
#[derive(Debug, Clone)]
pub struct Sort<T> {
    pub field: T,
    pub direction: SortDirection,
}

impl<T> Sort<T> {
    pub fn new(field: T, direction: SortDirection) -> Self {
        Self { field, direction }
    }

    pub fn asc(field: T) -> Self {
        Self::new(field, SortDirection::Ascending)
    }

    pub fn desc(field: T) -> Self {
        Self::new(field, SortDirection::Descending)
    }
}

/// Cursor for cursor-based pagination.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Cursor {
    /// Last item's ID
    pub last_id: String,
    /// Last item's creation timestamp
    pub last_created_at: DateTime<Utc>,
}

/// Paginated result wrapper.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaginatedResult<T> {
    /// Items on current page
    pub items: Vec<T>,
    /// Total number of items
    pub total: usize,
    /// Current page
    pub page: usize,
    /// Page size
    pub page_size: usize,
    /// Whether there are more pages
    pub has_next: bool,
    /// Whether there are previous pages
    pub has_previous: bool,
}

impl<T> PaginatedResult<T> {
    pub fn new(items: Vec<T>, total: usize, pagination: Pagination) -> Self {
        let total_pages = pagination.total_pages(total);
        Self {
            items,
            total,
            page: pagination.page,
            page_size: pagination.page_size,
            has_next: pagination.page < total_pages - 1,
            has_previous: pagination.page > 0,
        }
    }
}

/// Filter for query operations.
pub trait Filter<T>: Send + Sync {
    fn matches(&self, item: &T) -> bool;
}
