use reqwest::Client;
use oauth2::{basic::BasicClient, AuthUrl, ClientId, TokenUrl, ClientSecret, TokenResponse};

pub struct Integrations {
    client: Client,
    github_client: Option<BasicClient>,
    gitlab_client: Option<BasicClient>,
    sourceforge_api_key: Option<String>,
}

impl Integrations {
    pub fn new() -> Self {
        let github_client = BasicClient::new(
            ClientId::new("your-github-client-id".to_string()),
            Some(ClientSecret::new("your-github-client-secret".to_string())),
            AuthUrl::new("https://github.com/login/oauth/authorize".to_string()).unwrap(),
            Some(TokenUrl::new("https://github.com/login/oauth/access_token".to_string()).unwrap()),
        );

        let gitlab_client = BasicClient::new(
            ClientId::new("your-gitlab-client-id".to_string()),
            Some(ClientSecret::new("your-gitlab-client-secret".to_string())),
            AuthUrl::new("https://gitlab.com/oauth/authorize".to_string()).unwrap(),
            Some(TokenUrl::new("https://gitlab.com/oauth/token".to_string()).unwrap()),
        );

        Integrations {
            client: Client::new(),
            github_client: Some(github_client),
            gitlab_client: Some(gitlab_client),
            sourceforge_api_key: None,
        }
    }

    pub async fn fetch_github_repo(&self, repo: &str) -> Result<String, reqwest::Error> {
        let url = format!("https://api.github.com/repos/{}", repo);
        let response = self.client.get(&url).send().await?.text().await?;
        Ok(response)
    }

    pub async fn fetch_gitlab_project(&self, project_id: &str) -> Result<String, reqwest::Error> {
        let url = format!("https://gitlab.com/api/v4/projects/{}", project_id);
        let response = self.client.get(&url).send().await?.text().await?;
        Ok(response)
    }

    // SourceForge API wymaga niestandardowego podejścia
    pub async fn fetch_sourceforge_project(&self, project: &str) -> Result<String, reqwest::Error> {
        // TODO: Implementacja SourceForge API
        Ok(format!("SourceForge project: {}", project))
    }
}
