use anyhow::Result;
use lettre::transport::smtp::authentication::Credentials;
use lettre::{AsyncSmtpTransport, AsyncTransport, Message, Tokio1Executor};
use std::env;
use tracing::{info, instrument};
#[derive(Clone, Debug)]
pub struct MailSender {
    mailer: AsyncSmtpTransport<Tokio1Executor>,
    from_email: String,
    from_name: String,
}

impl MailSender {
    #[instrument(ret, err)]
    pub fn new() -> Result<Self> {
        let smtp_host = env::var("SMTP_SERVER")?;
        let smtp_username = env::var("EMAIL_ADDRESS")?;
        let smtp_password = env::var("EMAIL_PASSWORD")?;
        let from_email = env::var("EMAIL_ADDRESS")?;
        let from_name = env::var("EMAIL_NAME").unwrap_or_else(|_| "Sender".to_string());

        let creds = Credentials::new(smtp_username, smtp_password);

        let mailer = AsyncSmtpTransport::<Tokio1Executor>::relay(&smtp_host)?
            .credentials(creds)
            .build();

        Ok(Self {
            mailer,
            from_email,
            from_name,
        })
    }

    #[instrument(skip(self, body), ret, err)]
    pub async fn send_email(
        &self,
        to_email: &str,
        to_name: &str,
        subject: &str,
        body: &str,
    ) -> Result<()> {
        let from = format!("{} <{}>", self.from_name, self.from_email);
        let to = format!("{} <{}>", to_name, to_email);

        let email = Message::builder()
            .from(from.parse()?)
            .to(to.parse()?)
            .subject(subject)
            .body(body.to_string())?;

        self.mailer.send(email).await?;
        info!("✅ Email sent successfully to {}!", to_email);

        Ok(())
    }
}
