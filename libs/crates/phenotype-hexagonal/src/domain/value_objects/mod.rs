//! Value Objects - Immutable domain objects without identity
//! 
//! Value objects are immutable objects that describe some characteristic
//! or attribute but have no conceptual identity.
//!
//! ## Key Characteristics
//! 
//! - **Immutability**: Once created, cannot be changed
//! - **Value Equality**: Two value objects are equal if their values are equal
//! - **Side-Effect Free**: Operations return new instances
//!
//! ## When to Use
//! 
//! - Modeling measurements (Money, Weight, Distance)
//! - Modeling identifiers (Email, PhoneNumber)
//! - Modeling descriptions (Address, Name)
//!
//! ## Example
//! 
//! ```rust,ignore
//! #[derive(Clone, PartialEq, Eq)]
//! pub struct Money {
//!     amount: Decimal,
//!     currency: Currency,
//! }
//! 
//! impl Money {
//!     pub fn add(&self, other: Money) -> Result<Money, CurrencyMismatch> {
//!         // Returns new Money instance
//!     }
//! }
//! ```

pub mod value_object;
pub mod primitives;

pub use value_object::ValueObject;
pub use primitives::*;
