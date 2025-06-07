"""
This script provides an estimated token cost for a given text, 
using the GPT-3.5/4 encoding ("cl100k_base"). It does not include "thinking" tokens,
which can be used by the LLM for calculation, but are not part of the output.
While some LLM vendors offer token usage estimates, this is not standardized,
which is why this estimation is implemented.
"""

import tiktoken

# Change these to match your LLM costs
INPUT_TOKEN_COST_PER_MILLION = 1.25
OUTPUT_TOKEN_COST_PER_MILLION = 5


def calculate_token_costs(message: str):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(message)
    token_count = len(tokens)
    
    input_cost = (token_count / 1_000_000) * INPUT_TOKEN_COST_PER_MILLION
    output_cost = (token_count / 1_000_000) * OUTPUT_TOKEN_COST_PER_MILLION
    
    return token_count, input_cost, output_cost
