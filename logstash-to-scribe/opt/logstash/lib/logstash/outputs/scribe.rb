require "logstash/outputs/base"
require "logstash/namespace"

class LogStash::Outputs::Scribe < LogStash::Outputs::Base

  config_name "scribe"
  plugin_status "beta"

  # your scribe host
  config :host, :validate => :string, :required => true

  # the scribe port
  config :port, :validate => :number, :default => 1463

  # Allow overriding of the gelf 'sender' field. This is useful if you
  # want to use something other than the event's source host as the
  # "sender" of an event. A common case for this is using the application name
  # instead of the hostname.
  config :sender, :validate => :string, :default => "%{@source_host}"

  # The GELF message level. Dynamic values like %{level} are permitted here;
  # useful if you want to parse the 'log level' from an event and use that
  # as the gelf level/severity.
  #
  # Values here can be integers [0..7] inclusive or any of 
  # "debug", "info", "warn", "error", "fatal", "unknown" (case insensitive).
  # Single-character versions of these are also valid, "d", "i", "w", "e", "f",
  # "u"
  config :level, :validate => :array, :default => [ "%{severity}", "INFO" ]

  # The GELF facility. Dynamic values like %{foo} are permitted here; this
  # is useful if you need to use a value from the event as the facility name.
  config :facility, :validate => :string, :default => "logstash-gelf"

  # Ship metadata within event object?
  config :ship_metadata, :validate => :boolean, :default => true

  # The GELF custom field mappings. GELF supports arbitrary attributes as custom
  # fields. This exposes that. Exclude the `_` portion of the field name
  # e.g. `custom_fields => ['foo_field', 'some_value']
  # sets `_foo_field` = `some_value`
  config :custom_fields, :validate => :hash, :default => {}

  public
  def register
    require "scribe-rb"
    require "thrift"
    socket = Thrift::Socket.new( @host, @port)
    @transport = Thrift::FramedTransport.new(socket)
    @transport.open
    protocol = Thrift::BinaryProtocol.new(@transport, false)
    @client = Scribe::Client.new(protocol)
    @logger.debug("Created client conn #{@client.inspect}")
    @level_map = {
      "debug" => 7, "d" => 7,
      "info" => 6, "i" => 6,
      "warn" => 5, "w" => 5,
      "error" => 4, "e" => 4,
      "fatal" => 3, "f" => 3,
      "unknown" => 1, "u" => 1,
    }
  end # def register

  public
  def receive(event)
    return unless output?(event)

    m = Hash.new
    if event.fields["message"]
      v = event.fields["message"]
      m["short_message"] = (v.is_a?(Array) && v.length == 1) ? v.first : v
    else
      m["short_message"] = event.message
    end

    m["full_message"] = (event.message)
    
    m["host"] = event.sprintf(@sender)
    m["file"] = event["@source_path"]

    if @ship_metadata
        event.fields.each do |name, value|
          next if value == nil
          name = "_id" if name == "id"  # "_id" is reserved, so use "__id"
          if !value.nil?
            if value.is_a?(Array)
              # collapse single-element arrays, otherwise leave as array
              m["_#{name}"] = (value.length == 1) ? value.first : value
            else
              # Non array values should be presented as-is
              # https://logstash.jira.com/browse/LOGSTASH-113
              m["_#{name}"] = value
            end
          end
        end
    end

    if @custom_fields
      @custom_fields.each do |field_name, field_value|
        m["_#{field_name}"] = field_value unless field_name == 'id'
      end
    end

    # set facility as defined
    m["facility"] = event.sprintf(@facility)

    # Probe severity array levels
    level = nil
    if @level.is_a?(Array)
      @level.each do |value|
        parsed_value = event.sprintf(value)
        if parsed_value
          level = parsed_value
          break
        end
      end
    else
      level = event.sprintf(@level.to_s)
    end
    m["level"] = (@level_map[level.downcase] || level).to_i
    m["version"] = "2.0"

    @logger.debug("Sending event")
    log_entry = LogEntry.new(:category => 'default', :message  => (m.to_json))
    
    result = @client.Log([log_entry]) 
    @logger.debug("send #{log_entry.inspect} result: #{result.inspect}") 

  end # def receive
  def teardown
    @transport.close
  end # def teardown
end # class LogStash::Outputs::Scribe
