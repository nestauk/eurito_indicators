import logging
import json
from pathlib import Path

from metaflow import Run

from eurito_indicators import get_yaml_config, PROJECT_DIR
from eurito_indicators.utils.metaflow_runner import update_model_config, execute_flow
from industrial_taxonomy.flows.classifier.classifier_utils import create_org_data 

logger = logging.getLogger(__name__)

def preprocess():
    FLOW_ID = "sic_preprocessing"
    CONFIG_ID = "sic4_preprocessing"

    task_config = config["flows"][CONFIG_ID]

    flow_config = {
            '--sic_level': str(task_config['sic_level']),
            '--match_threshold': str(task_config['match_threshold']),
            '--test': str(task_config["test"]),
            '--config': json.dumps(task_config['config'])
            }
    flow_file = Path(__file__).resolve().parents[0] / f"{FLOW_ID}.py"
    run_id = execute_flow(
            flow_file,
            flow_config,
            metaflow_args={}
            )

    task_config["run_id"] = run_id
    update_model_config(["flows", CONFIG_ID], task_config)
    return run_id

if __name__ == "__main__":
    preprocess_run_id = preprocess() 
    preprocess_run = Run(f"SicPreprocess/{preprocess_run_id}")

    FLOW_ID = "classifier_train"
    CONFIG_ID = "sic4_classifier"
    task_config = config["flows"][CONFIG_ID]
    output_dir = task_config["config"]["training_args"]["output_dir"]
    task_config["config"]["training_args"]["output_dir"] = str(project_dir / output_dir)
    
    documents_path = str(project_dir / task_config['documents_path'])

    with open(documents_path, 'w') as f:
        json.dump(preprocess_run.data.train_set, f)

    flow_config = {
            '--documents_path': documents_path,
            '--freeze_model': str(task_config['freeze_model']),
            '--config': json.dumps(task_config['config'])
            }

    flow_file = Path(__file__).resolve().parents[0] / f"{FLOW_ID}.py"
    run_id = execute_flow(
            flow_file,
            flow_config,
            metaflow_args={}
            )

    task_config["run_id"] = run_id
    task_config["config"]["training_args"]["output_dir"] = output_dir
    update_model_config(["flows", CONFIG_ID], task_config)