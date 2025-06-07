import datetime
from llm_to_json.llm_to_json import llm_to_json
from json_to_graph.json_to_graph import json_to_graph
from logger import get_logger, logg_print

start_time = datetime.datetime.now()
logger = get_logger()

llm_to_json(logger)
json_to_graph(logger)

end_time = datetime.datetime.now()
elapsed = end_time - start_time  # This is a timedelta object

# Format timedelta as HH:MM:SS
formatted_time = str(elapsed).split('.')[0]  # Remove microseconds part

logg_print(logger, f"⏱️ Total execution time: {formatted_time}")
