//! Presenters
//! 
//! Format data for presentation to the user.

/// Presenter trait
pub trait Presenter<V, R>: Send + Sync {
    fn present(&self, view_model: V) -> R;
}

/// HTML presenter
pub struct HtmlPresenter;

impl Presenter<String, String> for HtmlPresenter {
    fn present(&self, view_model: String) -> String {
        format!("<html><body>{}</body></html>", view_model)
    }
}

/// JSON presenter
pub struct JsonPresenter;

impl Presenter<serde_json::Value, String> for JsonPresenter {
    fn present(&self, view_model: serde_json::Value) -> String {
        serde_json::to_string(&view_model).unwrap_or_default()
    }
}
