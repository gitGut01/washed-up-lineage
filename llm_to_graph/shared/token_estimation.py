import tiktoken

# Change these to match your LLM costs
INPUT_TOKEN_COST_PER_MILLION = 1.25
OUTPUT_TOKEN_COST_PER_MILLION = 5


def calculate_token_costs(message: str):
    # Use tiktoken to count tokens (GPT-3.5/4 encoding is "cl100k_base")
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(message)
    token_count = len(tokens)
    
    input_cost = (token_count / 1_000_000) * INPUT_TOKEN_COST_PER_MILLION
    output_cost = (token_count / 1_000_000) * OUTPUT_TOKEN_COST_PER_MILLION
    
    return token_count, input_cost, output_cost
