use reqwest::Client;
use oauth2::{basic::BasicClient, TokenResponse};

pub struct Integrations {
    client: Client,
    github_client: Option<BasicClient>,
}

impl Integrations {
    pub fn new() -> Self {
        let github_client = BasicClient::new(
            ClientId::new("your-github-client-id".to_string()),
            None,
            AuthUrl::new("https://github.com/login/oauth/authorize".to_string()).unwrap(),
            Some(TokenUrl::new("https://github.com/login/oauth/access_token".to_string()).unwrap()),
        );

        Integrations {
            client: Client::new(),
            github_client: Some(github_client),
        }
    }

    pub async fn fetch_github_repo(&self, repo: &str) -> Result<String, reqwest::Error> {
        let url = format!("https://api.github.com/repos/{}", repo);
        let response = self.client.get(&url).send().await?.text().await?;
        Ok(response)
    }
}
