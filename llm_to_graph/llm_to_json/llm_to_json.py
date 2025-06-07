import datetime
import glob
import json
import os
import time
from collections import defaultdict
from pathlib import Path

import tqdm
from pydantic import BaseModel

from data_models import DataModel, DataModelSimple, StoredProcedure, StoredProcedureSimple
from llm_to_json.llm_client.llm_client import LLMClient
from llm_to_json.sql_datamodel_extraction.feedback import feedback_template as datamodel_feedback_template
from llm_to_json.sql_datamodel_extraction.prompt import prompt as datamodel_prompt
from llm_to_json.sql_datamodel_extraction.prompt_simple import prompt_simple as datamodel_simple_prompt
from llm_to_json.sql_stored_procedure_extraction.feedback import feedback_template as stored_procedure_feedback_template
from llm_to_json.sql_stored_procedure_extraction.prompt import prompt as stored_procedure_prompt
from llm_to_json.sql_stored_procedure_extraction.prompt_simple import prompt_simple as stored_procedure_simple_prompt
from llm_to_json.token_estimation import (
    calculate_token_costs,
    INPUT_TOKEN_COST_PER_MILLION,
    OUTPUT_TOKEN_COST_PER_MILLION,
)
from llm_to_json.validation import validate_output

from logger import logg_print
from config import(
    DEFAULT_EXTRACTION_DIR,
    PATH_EXTRACTION_RUNS,
    DATAMODEL_SQL_PATHTS,
    STORED_PROCEDURE_SQL_PATHS,
    DO_SIMPLE_EXTRACT
)

DO_COST_ESTIMATE_WITHOUT_LLM = True

llm_client = LLMClient()
initialized_llm = llm_client.get_model()

all_stats = []

stats = {
    "loaded_file_count": 0,
    "use_ai_file_count": 0,
    "success_count": 0,
    "error_count": 0,
    "warning_count": 0,
    "token_in_count": 0,
    "token_out_count": 0,
    "cost_in": 0,
    "cost_out": 0
}


def get_ouput_file_dir(sql_file_path: str):
    sql_file_path = str(sql_file_path.parent).lstrip('.').lstrip('/')

    output_file_dir = os.path.join(DEFAULT_EXTRACTION_DIR, PATH_EXTRACTION_RUNS, sql_file_path)
    return output_file_dir

def save_extraction_to_file(parsed_model_class: BaseModel, sql_file_path: str, attempt: int, logger) -> bool:
    base_name = sql_file_path.stem
    output_file_dir = get_ouput_file_dir(sql_file_path)
    os.makedirs(output_file_dir, exist_ok=True)
    json_file_path = os.path.join(output_file_dir, f"{base_name}.sql_response_{attempt}.json")

    try:
        save_data = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "attempt": attempt,
                "sql_file": str(sql_file_path)
            },
            "data": parsed_model_class.model_dump()
        }
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
        return True
        
    except Exception as e:

        logger.warning(f"Failed to save response to file: {str(e)}")
        return False


def extract_first_attempt(sql_script, prompt_template):
    extraction_chain = prompt_template | initialized_llm
    response = extraction_chain.invoke({"sql_script": sql_script})
    return response


def extract_fallback(
    previous_output, 
    sql_script,
    last_error,
    model_class,
    feedback_template
):
    feedback_chain = feedback_template | initialized_llm
    response = feedback_chain.invoke({
        "sql_script": sql_script,
        "previous_output": previous_output,
        "error_message": last_error,
        "schema": model_class.schema_json(indent=2)
    })

    return response


def get_latest_extraction_file_path(sql_file_path):
    base_name = sql_file_path.stem
    output_file_dir = get_ouput_file_dir(sql_file_path)

    pattern = os.path.join(output_file_dir, f"{base_name}.sql_response_*.json")
    matches = glob.glob(pattern, recursive=True)
    matches.sort()

    if not matches: return None
    return matches[-1]


def get_latest_extraction(sql_file_path):
    latest_extraction_file_path = get_latest_extraction_file_path(sql_file_path)
    if latest_extraction_file_path is None: return None
    with open(latest_extraction_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    data_part = json_data.get("data", {})
    return json.dumps(data_part, indent=2)


def extract_single_sql(
    sql_file_path, 
    prompt_template,
    feedback_template,
    model_class,
    max_attempts,
    logger
):
    previous_output = None
    last_error = None
    logger.info(f"Extract with LLM: {sql_file_path}")
    with open(sql_file_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()    

        for attempt in range(max_attempts):
            if attempt == 0:
                response = extract_first_attempt(sql_script, prompt_template)
                full_prompt = prompt_template.format_prompt(sql_script=sql_script)
            else:
                logger.warning(f"Retry {attempt}/{max_attempts} with self-correction...")
                stats['warning_count'] += 1
                response = extract_fallback(previous_output, sql_script, last_error, model_class, feedback_template)
                full_prompt = f"{str(feedback_template)}\n{previous_output}\n{last_error}\n{model_class.schema_json(indent=2)}"
            
            token_in_count, input_cost, _ = calculate_token_costs(str(full_prompt))
            token_out_count, _, output_cost = calculate_token_costs(str(response))
            stats['token_in_count'] += token_in_count
            stats['cost_in'] += input_cost
            stats['token_out_count'] += token_out_count
            stats['cost_out'] += output_cost

            response_content = response.content if hasattr(response, 'content') else str(response)
            success, error, parsed_json = validate_output(response_content, model_class)

            if success:
                parsed_model_class = model_class(**parsed_json)
                save_extraction_to_file(parsed_model_class, sql_file_path, attempt+1, logger)
                stats['use_ai_file_count'] += 1
                stats['success_count'] += 1
                logger.info(f"🧠 Success validating from LLM output: {sql_file_path}")
                return

            else:
                previous_output = response_content
                last_error = error
                logger.warning(f"Failed: {sql_file_path}")

    stats['error_count'] += 1
    error_message = f"Failed after {max_attempts} attempts. Last error: {last_error}"
    logger.error(error_message)


def set_pbar_postfix(pbar):
    postfix_str = (
        f"📁{stats['loaded_file_count']} " +
        f"🧠{stats['use_ai_file_count']} - 💬{stats['token_in_count']}/{stats['token_out_count']} " +
        f"💸${stats['cost_in']:.2f}/${stats['cost_out']:.2f} " +
        f"✅{stats['success_count']} | ⚠️ {stats['warning_count']} | ❌{stats['error_count']}"
    )
    pbar.set_postfix_str(postfix_str)
    return postfix_str


def loop_through_all_sqls(
    sql_path_dir, 
    prompt_template,
    feedback_template,
    model_class,
    max_attempts = 3,
    logger = None
):
    global stats
    stats = {key: 0 for key in stats}
    sql_file_paths = list(Path(sql_path_dir).glob('**/*.sql'))

    with tqdm.tqdm(sql_file_paths) as pbar:
        for sql_file_path in pbar:
            latest_extraction_content = get_latest_extraction(sql_file_path)
            if latest_extraction_content is not None: 
                success, _, _ = validate_output(latest_extraction_content, model_class)
                if success:
                    logger.info(f"📁 Success validated from file: {sql_file_path}")
                    if DO_COST_ESTIMATE_WITHOUT_LLM:
                        with open(sql_file_path, 'r', encoding='utf-8') as file:
                            sql_script = file.read()
                        token_in_count, input_cost, _ = calculate_token_costs(str(prompt_template) + str(sql_script))
                        token_out_count, _, output_cost = calculate_token_costs(str(latest_extraction_content))
                        stats['token_in_count'] += token_in_count
                        stats['cost_in'] += input_cost
                        stats['token_out_count'] += token_out_count
                        stats['cost_out'] += output_cost
                    
                    stats['loaded_file_count'] += 1
                    stats['success_count'] += 1
                    set_pbar_postfix(pbar)
                    continue

            extract_single_sql(sql_file_path, prompt_template, feedback_template, model_class, max_attempts, logger)
            set_pbar_postfix(pbar)

        final_postfix = set_pbar_postfix(pbar)
        logger.info(f"{final_postfix}\n")

    all_stats.append(stats)
    print()




def logg_all_stats(start_time, logger):
    end_time = time.time()
    elapsed_seconds = end_time - start_time

    total_stats = defaultdict(int)
    for stat in all_stats:
        for key, value in stat.items():
            total_stats[key] += value

    messages = [
        "===== LLM to JSON STATS =====",
        f"⏱️  Execution time: {elapsed_seconds:.2f} seconds\n",
        f"📁 Loaded from files: {total_stats['loaded_file_count']}",
        f"🧠 Used AI for extraction: {total_stats['use_ai_file_count']}",
        f"💬 Token used (in/out): {total_stats['token_in_count']}/{total_stats['token_out_count']} (Assuming per million: ${INPUT_TOKEN_COST_PER_MILLION}/${OUTPUT_TOKEN_COST_PER_MILLION})",
        f"💸 Token costs (in/out): ${total_stats['cost_in']:.2f}/${total_stats['cost_out']:.2f} -> Total: ${(total_stats['cost_in'] + total_stats['cost_out']):.2f}",
        f"✅ Success: {total_stats['success_count']}",
        f"⚠️  Warnings: {total_stats['warning_count']}",
        f"❌ Errors: {total_stats['error_count']}\n"
    ]
    for msg in messages:
        logg_print(logger, msg)

def llm_to_json(logger):
    logg_print(logger, "----- LLM to JSON ----")
    start_time = time.time()
    logg_print(logger, f"DO_COST_ESTIMATE_WITHOUT_LLM: {DO_COST_ESTIMATE_WITHOUT_LLM}\n")

    for path in DATAMODEL_SQL_PATHTS:
        logg_print(logger, f"Processing datamodels in {path}")
        prompt_template = datamodel_simple_prompt if DO_SIMPLE_EXTRACT else datamodel_prompt
        model_class = DataModelSimple if DO_SIMPLE_EXTRACT else DataModel
        loop_through_all_sqls(path, prompt_template, datamodel_feedback_template, model_class, logger=logger)

    for path in STORED_PROCEDURE_SQL_PATHS:
        logg_print(logger, f"Processing stored procedures in {path}")
        prompt_template = stored_procedure_simple_prompt if DO_SIMPLE_EXTRACT else stored_procedure_prompt
        model_class = StoredProcedureSimple if DO_SIMPLE_EXTRACT else StoredProcedure
        loop_through_all_sqls(path, prompt_template, stored_procedure_feedback_template, model_class, logger=logger)

    logg_all_stats(start_time, logger)
