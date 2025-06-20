use reqwest::Client;
use oauth2::{basic::BasicClient, AuthUrl, ClientId, TokenUrl};

#[derive(Clone)]
pub struct Assistant {
    client: Client,
    github_client: Option<BasicClient>,
    gitlab_client: Option<BasicClient>,
    sourceforge_client: Option<BasicClient>,
}

impl Assistant {
    pub fn new() -> Self {
        // Przykład konfiguracji OAuth dla GitHub
        let github_client = BasicClient::new(
            ClientId::new("your-github-client-id".to_string()),
            None,
            AuthUrl::new("https://github.com/login/oauth/authorize".to_string()).unwrap(),
            Some(TokenUrl::new("https://github.com/login/oauth/access_token".to_string()).unwrap()),
        );

        Assistant {
            client: Client::new(),
            github_client: Some(github_client),
            gitlab_client: None, // TODO: GitLab OAuth
            sourceforge_client: None, // TODO: SourceForge OAuth
        }
    }

    pub async fn handle_request(&self, query: String, mode: i32) -> String {
        match mode {
            1 => self.web_search(&query).await,
            2 => self.developer_mode(&query).await,
            _ => self.conversation(&query).await,
        }
    }

    async fn conversation(&self, query: &str) -> String {
        // TODO: Połączenie z Grok API (https://x.ai/api)
        format!("Sava AI: How can I assist you with '{}'? Try asking about coding or web searches!", query)
    }

    async fn web_search(&self, query: &str) -> String {
        let url = format!("https://www.startpage.com/sp/search?query={}", urlencoding::encode(query));
        let response = self.client.get(&url).send().await.unwrap().text().await.unwrap();
        format!("Search results for '{}': {}", query, response.chars().take(100).collect::<String>())
    }

    async fn developer_mode(&self, query: &str) -> String {
        if query.starts_with("github:") {
            let repo = query.strip_prefix("github:").unwrap().trim();
            let url = format!("https://api.github.com/repos/{}", repo);
            let response = self.client.get(&url).send().await.unwrap().text().await.unwrap();
            return format!("GitHub repo info for '{}': {}", repo, response.chars().take(100).collect::<String>());
        }
        // TODO: GitLab, SourceForge
        format!("Developer mode: Processing '{}'. Try 'github:owner/repo'!", query)
    }
}
