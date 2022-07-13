import os

from iquaflow.datasets import DSWrapper
from iquaflow.experiments import ExperimentSetup
from iquaflow.experiments.task_execution import PythonScriptTaskExecution

from custom_iqf import (
    DSModifierResize,
    DSModifier_jpg,
    DSModifier_quant
    )

jpgmod = [DSModifier_jpg(params={"quality": quality}) for quality in range(10,100,10)]
quantmod = [DSModifier_quant(params={"bits": bits}) for bits in range(1,9)]
resizemod = [DSModifierResize(params={"scaleperc": perc}) for perc in range(10,100,10)]

combo_mod_lst = []
for quality in range(20,90,20):
    for bits in range(2,10,2):
        for perc in range(20,100,20):
            combo_mod_lst.append( 
                DSModifier_jpg(
                    ds_modifier=DSModifier_quant(
                        ds_modifier=DSModifierResize(
                            params={"scaleperc": perc}
                            ),
                        params={"bits": bits}
                        ),
                    params={"quality": quality}
                    )
                )

for model,cropsz in zip([
    '/iqf/dota_rfcn_output_2000000_136610/frozen_inference_graph.pb',
    # '/iqf/dota608_ssd608_output_1243788/frozen_inference_graph.pb'
],[
    1024,
    # 608
]):

    #Experiment definition, pass as arguments all the components defined beforehand
    experiment = ExperimentSetup(
        experiment_name         = "iq-dota-use-case",
        task_instance           = PythonScriptTaskExecution( model_script_path = './inference.py' ),
        ref_dsw_train           = DSWrapper(data_path=f'/Nas/DOTA1_0/split_ss_dota1_0_glasgow_{cropsz}/val'),
        ds_modifiers_list       = [
            DSModifier_jpg(params={"quality": quality}) for quality in range(90,101,2)
        ] + [
            DSModifier_jpg(params={"quality": quality}) for quality in range(10,100,10)
        ] + [
            DSModifier_quant(params={"bits": bits}) for bits in range(1,9)
        ] + [
            DSModifierResize(params={"scaleperc": perc}) for perc in range(10,110,10)
        ] + [
            # *combo_mod_lst
        ],
        repetitions             = 1,
        cloud_options           = {
            'tracking_uri':'https://mlflow.ml.analytics-dev.satellogic.team/'
        },
        extra_train_params      = {
            'model':[model],
            'cu':['0,1,2']
            }
    )

    #Execute the experiment
    experiment.execute()
