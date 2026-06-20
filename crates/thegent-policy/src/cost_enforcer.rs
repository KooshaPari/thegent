// SPDX-License-Identifier: MIT OR Apache-2.0
use std::sync::{Arc, Mutex};

pub struct CostEnforcer {
    daily_limit: f64,
    spent: Arc<Mutex<f64>>,
}

impl CostEnforcer {
    pub fn new(daily_limit: f64) -> Self {
        Self {
            daily_limit,
            spent: Arc::new(Mutex::new(0.0)),
        }
    }

    pub fn check_budget_available(&self, amount: f64) -> Result<bool, PolicyBudgetError> {
        let spent = *self
            .spent
            .lock()
            .map_err(|_| PolicyBudgetError::LockPoisoned)?;
        Ok(spent + amount <= self.daily_limit)
    }

    pub fn can_spend(&self, amount: f64) -> bool {
        let mut spent = self.spent.lock().expect("lock poisoned");
        if *spent + amount <= self.daily_limit {
            *spent += amount;
            true
        } else {
            false
        }
    }

    pub fn reset(&self) {
        *self.spent.lock().expect("lock poisoned") = 0.0;
    }

    pub fn remaining(&self) -> f64 {
        let spent = *self.spent.lock().expect("lock poisoned");
        self.daily_limit - spent
    }
}

impl Clone for CostEnforcer {
    fn clone(&self) -> Self {
        Self {
            daily_limit: self.daily_limit,
            spent: Arc::clone(&self.spent),
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub enum PolicyBudgetError {
    #[error("Mutex lock poisoned")]
    LockPoisoned,
}
