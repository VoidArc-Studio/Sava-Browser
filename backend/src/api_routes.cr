require "kemal"

get "/api/adblock/filter/:url" do |env|
  url = env.params.url
  AdBlocker.filter_request(url).to_s
end

post "/api/ai/query" do |env|
  prompt = env.params.json["prompt"].as_s
  AIIntegration.query_grok(prompt)
end
