require "http/client"

module AdBlocker
  AD_BLOCK_LIST = File.read_lines("../config/ad_block_lists.txt")

  def self.filter_request(url : String) : Bool
    AD_BLOCK_LIST.any? { |pattern| url.match(Regex.new(pattern)) }
  end
end
