//! Money value object
//! 
//! Represents monetary values with currency.

use std::fmt;
use std::error::Error;
use serde::{Serialize, Deserialize};

#[derive(Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Money {
    cents: i64,
    currency: Currency,
}

#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug, Serialize, Deserialize)]
pub enum Currency {
    USD,
    EUR,
    GBP,
}

#[derive(Debug)]
pub enum MoneyError {
    CurrencyMismatch(Currency, Currency),
    NegativeAmount,
}

impl fmt::Display for MoneyError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            MoneyError::CurrencyMismatch(a, b) => {
                write!(f, "Currency mismatch: {:?} vs {:?}", a, b)
            }
            MoneyError::NegativeAmount => write!(f, "Money cannot be negative"),
        }
    }
}

impl Error for MoneyError {}

impl Money {
    pub fn new(cents: i64, currency: Currency) -> Result<Self, MoneyError> {
        if cents < 0 {
            return Err(MoneyError::NegativeAmount);
        }
        Ok(Self { cents, currency })
    }
    
    pub fn usd(cents: i64) -> Result<Self, MoneyError> {
        Self::new(cents, Currency::USD)
    }
    
    pub fn eur(cents: i64) -> Result<Self, MoneyError> {
        Self::new(cents, Currency::EUR)
    }
    
    pub fn pounds(cents: i64) -> Result<Self, MoneyError> {
        Self::new(cents, Currency::GBP)
    }
    
    pub fn currency(&self) -> Currency {
        self.currency
    }
    
    pub fn cents(&self) -> i64 {
        self.cents
    }
    
    pub fn add(&self, other: &Money) -> Result<Money, MoneyError> {
        if self.currency != other.currency {
            return Err(MoneyError::CurrencyMismatch(self.currency, other.currency));
        }
        Money::new(self.cents + other.cents, self.currency)
    }
    
    pub fn subtract(&self, other: &Money) -> Result<Money, MoneyError> {
        if self.currency != other.currency {
            return Err(MoneyError::CurrencyMismatch(self.currency, other.currency));
        }
        let result = self.cents - other.cents;
        if result < 0 {
            return Err(MoneyError::NegativeAmount);
        }
        Money::new(result, self.currency)
    }
}

impl fmt::Debug for Money {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Money({:.2} {:?})", self.cents as f64 / 100.0, self.currency)
    }
}

impl fmt::Display for Currency {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Currency::USD => write!(f, "USD"),
            Currency::EUR => write!(f, "EUR"),
            Currency::GBP => write!(f, "GBP"),
        }
    }
}
