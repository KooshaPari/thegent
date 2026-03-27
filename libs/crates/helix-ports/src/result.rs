//! Result type for ports operations

use crate::outbound::{RepositoryError, PublisherError, ClientError, CacheError};
use crate::error::PortError;

/// Alias for port operation results
pub type PortResult<T> = Result<T, PortError>;

/// Alias for repository results
pub type RepoResult<T> = Result<T, RepositoryError>;

/// Alias for publisher results
pub type PubResult<T> = Result<T, PublisherError>;

/// Alias for client results
pub type ClientResult<T> = Result<T, ClientError>;

/// Alias for cache results
pub type CacheResult<T> = Result<T, CacheError>;
