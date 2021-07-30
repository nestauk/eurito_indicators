import importlib
import yaml

from sklearn.pipeline import Pipeline

from eurito_indicators import PROJECT_DIR
from eurito_indicators.utils.sdg_utils import stringify_sdg_number


def sklearn_pipeline_to_config(pipeline, sdg):
    """Saves the parameters of a scikit-learn pipeline to a yaml config file.

        For example:

        clf = Pipeline(steps=[
            ('scaler', StandardScaler(with_mean=True)),
            ('lr', LinearRegression(C=10))
        ])

        would yield a config containing

        scaler:
          estimator_class_name: StandardScaler
          estimator_module_name: sklearn.preprocessing
            params:
              with_mean: true
        lr:
          estimator_class_name: LineaRegression
          estimator_module_name: sklearn.linear_model
          params:
            C: 10
    
    Args:
        pipeline (Pipeline): A trained pipeline.
        sdg (int): The SDG this pipeline is trained to predict.

    """
    pipe_config = {}

    for step_name, step in pipeline.steps:
        step_config = {
            'estimator_class_name': step.__class__.__name__,
            'estimator_module': step.__module__
        }
        
        params = step.get_params()
        params = {f'{step_name}__{k}': v for k, v in params.items()}
        step_config['params'] = params
        pipe_config[step_name] = step_config

    sdg = stringify_sdg_number(sdg)
    config_path = f'{PROJECT_DIR}/eurito_indicators/config/sdg/classifier/sdg_{sdg}.yaml'

    with open(config_path, 'w') as fout:
        yaml.dump(pipe_config, fout)


def sklearn_pipeline_from_config(config_path):
    """Constructs a scikit-learn Pipeline from parameters specified in a yaml
    config file.
    
    Args:
        config_path (str): Path to the config yaml with the pipeline parameters

    Returns:
        (Pipeline): An untrained scikit-learn pipeline instantiated with 
            paramters from the config file.
    """
    with open(config_path, 'r') as fin:
        config = yaml.load(fin, Loader=yaml.UnsafeLoader)

    steps = []
    for step_name, step in config.items():
        estimator_ = importlib(step['module'], step['class_name'])
        steps.append((step_name, estimator_(**step['params'])))

    return Pipeline(steps)

def make_sdg_pipeline(sdg):
    """Wrapper function to automatically make a model pipeline with only the 
    SDG number."""
    sdg = stringify_sdg_number(sdg)
    config_path = f'{PROJECT_DIR}/eurito_indicators/config/sdg/classifier/sdg_{sdg}.yaml'
    return sklearn_pipeline_from_config(config_path)
