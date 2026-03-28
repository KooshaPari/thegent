//! Retry strategies for API requests.
//!
//! This module provides configurable retry strategies.

use crate::domain::{ApiError, ApiResult, Response};
use std::time::Duration;

/// Retry strategy for handling transient failures.
#[derive(Debug, Clone)]
pub enum RetryStrategy {
    /// Never retry.
    None,
    /// Fixed number of retries with fixed delay.
    Fixed { max_attempts: u32, delay_ms: u64 },
    /// Exponential backoff with jitter.
    Exponential {
        max_attempts: u32,
        base_delay_ms: u64,
        max_delay_ms: u64,
        jitter_ms: u64,
    },
    /// Linear backoff.
    Linear {
        max_attempts: u32,
        start_delay_ms: u64,
        increment_ms: u64,
    },
}

impl RetryStrategy {
    /// Never retry.
    pub fn none() -> Self {
        Self::None
    }

    /// Fixed retry with delay.
    pub fn fixed(max_attempts: u32, delay_ms: u64) -> Self {
        Self::Fixed { max_attempts, delay_ms }
    }

    /// Exponential backoff with optional jitter.
    pub fn exponential(max_attempts: u32, base_delay_ms: u64) -> Self {
        Self::Exponential {
            max_attempts,
            base_delay_ms,
            max_delay_ms: 60_000, // 1 minute max
            jitter_ms: 100,
        }
    }

    /// Linear backoff.
    pub fn linear(max_attempts: u32, start_delay_ms: u64, increment_ms: u64) -> Self {
        Self::Linear {
            max_attempts,
            start_delay_ms,
            increment_ms,
        }
    }

    /// Calculate delay for a given attempt.
    pub fn delay(&self, attempt: u32) -> Option<Duration> {
        match self {
            Self::None => None,
            Self::Fixed { delay_ms, .. } => Some(Duration::from_millis(*delay_ms)),
            Self::Exponential {
                base_delay_ms,
                max_delay_ms,
                jitter_ms,
                ..
            } => {
                if attempt == 0 {
                    return Some(Duration::from_millis(*base_delay_ms));
                }
                let delay = std::cmp::min(
                    base_delay_ms * 2u64.pow(attempt - 1),
                    *max_delay_ms,
                );
                let jitter = if *jitter_ms > 0 {
                    (rand_u64() % *jitter_ms) as i64
                } else {
                    0
                };
                Some(Duration::from_millis((delay as i64 + jitter).max(0) as u64))
            }
            Self::Linear {
                start_delay_ms,
                increment_ms,
                ..
            } => {
                if attempt == 0 {
                    return Some(Duration::from_millis(*start_delay_ms));
                }
                Some(Duration::from_millis(
                    start_delay_ms + increment_ms * (attempt as u64 - 1),
                ))
            }
        }
    }

    /// Get max attempts.
    pub fn max_attempts(&self) -> u32 {
        match self {
            Self::None => 1,
            Self::Fixed { max_attempts, .. } => *max_attempts,
            Self::Exponential { max_attempts, .. } => *max_attempts,
            Self::Linear { max_attempts, .. } => *max_attempts,
        }
    }

    /// Check if should retry based on error or response.
    pub fn should_retry(&self, attempt: u32, result: &ApiResult<Response>) -> bool {
        if attempt >= self.max_attempts() {
            return false;
        }

        match result {
            // Retry on connection errors
            Err(e) => matches!(
                e.code(),
                crate::domain::ApiErrorCode::Timeout |
                crate::domain::ApiErrorCode::ConnectionError |
                crate::domain::ApiErrorCode::DnsError |
                crate::domain::ApiErrorCode::GatewayTimeout
            ),
            // Retry on 5xx server errors
            Ok(response) => {
                matches!(
                    response.status(),
                    crate::domain::http::StatusCode::InternalServerError |
                    crate::domain::http::StatusCode::BadGateway |
                    crate::domain::http::StatusCode::ServiceUnavailable |
                    crate::domain::http::StatusCode::GatewayTimeout
                )
            }
        }
    }
}

impl Default for RetryStrategy {
    fn default() -> Self {
        Self::exponential(3, 100)
    }
}

/// Simple random u64 for jitter (avoiding external dependencies).
fn rand_u64() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .subsec_nanos() as u64;
    nanos.wrapping_mul(1103515245).wrapping_add(12345)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_none_strategy() {
        let strategy = RetryStrategy::none();
        assert_eq!(strategy.max_attempts(), 1);
        assert!(strategy.delay(0).is_none());
    }

    #[test]
    fn test_fixed_strategy() {
        let strategy = RetryStrategy::fixed(3, 100);
        assert_eq!(strategy.max_attempts(), 3);
        assert_eq!(strategy.delay(0), Some(Duration::from_millis(100)));
    }

    #[test]
    fn test_exponential_strategy() {
        let strategy = RetryStrategy::exponential(3, 100);
        assert_eq!(strategy.max_attempts(), 3);
        // First attempt: 100ms, second: 200ms, third: 400ms
        assert_eq!(strategy.delay(0), Some(Duration::from_millis(100)));
        assert!(strategy.delay(1).unwrap() <= Duration::from_millis(300)); // 200 + jitter
    }
}
