require "http/client"
require "json"

module AIIntegration
  API_KEY = ENV["GROK_API_KEY"]?

  def self.query_grok(prompt : String) : String
    return "API key not set" unless API_KEY
    response = HTTP::Client.post(
      "https://api.x.ai/v1/grok",
      headers: HTTP::Headers{"Authorization" => "Bearer #{API_KEY}"},
      body: {"prompt" => prompt}.to_json
    )
    JSON.parse(response.body)["response"]?.to_s
  end
end
