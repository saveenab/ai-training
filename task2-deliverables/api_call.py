import anthropic

client = anthropic.Anthropic(api_key="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")

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "Hello, what is an AI agent?"}
    ]
)   
print(message.content[0].text)