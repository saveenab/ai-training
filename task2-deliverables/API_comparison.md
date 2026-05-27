# API Comparison Table

## Anthropic API vs. OpenAI API vs. Amazon Bedrock

| Feature | Anthropic API | OpenAI API | Amazon Bedrock |
|---|---|---|---|
| Models Available | Claude (Haiku, Sonnet, Opus) | GPT-4, GPT-3.5, o1 | Claude, Llama, Titan, Mistral, Cohere |
| Pricing | Per token (input/output) | Per token (input/output) | Per token (slightly higher due to AWS markup) |
| Strengths | Safety, long context window, strong reasoning | Large ecosystem, wide tool support, plugins | Multi-model access, AWS integration, enterprise ready |
| Context Window | Up to 1M tokens (Sonnet 4.6) | Up to 128k tokens (GPT-4) | Varies by model |
| Authentication | API Key | API Key | AWS IAM credentials |
| Python SDK | anthropic | openai | boto3 |
| Setup Difficulty | Easy | Easy | Medium (requires AWS account and IAM setup) |
| Best For | Safe reliable AI agents, long documents | General purpose, large developer ecosystem | Enterprise AWS workloads, multi-model flexibility |
| Fine-tuning | Not available | Available | Available for some models |
| RAG Support | Via API + external vector store | Via API + external vector store | Built-in via Bedrock Knowledge Bases |
| Free Tier | No (pay per use) | Limited free credits | AWS free tier (limited) |