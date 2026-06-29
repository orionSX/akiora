use anyhow::Result;

use tracing::info;
use tracing_subscriber::{fmt, layer::SubscriberExt, util::SubscriberInitExt};

pub fn init_tracing() -> Result<()> {
    let fmt_layer = fmt::layer()
        .with_target(true)
        .with_thread_ids(true)
        .with_thread_names(true)
        .with_file(true)
        .with_line_number(true)
        .with_level(true)
        .pretty()
        .with_writer(std::io::stdout);

    tracing_subscriber::registry()
        .with(fmt_layer)
        .try_init()
        .map_err(|e| anyhow::anyhow!("Failed to initialize tracing: {}", e))?;

    info!("Tracing initialized successfully");
    Ok(())
}
