import os
import yaml

from util.processing_sequence import ProcessingSequence


class PlanManager:

    @staticmethod
    def save_processing_plan(plan_dir, plan_name, sequence):
        if not os.path.exists(plan_dir):
            os.makedirs(plan_dir)
        file = plan_name
        sequence_save_list = []
        for i, step in enumerate(sequence):
            step_param = {"processing_name": step.step_text, "processing_input_number": step.step_input_number}
            param_key_list = step.attribute.get_params_key()
            for param_key in param_key_list:
                step_param[param_key] = step.attribute.get_plan_param_value(param_key)
            sequence_save_list.append(step_param)
        plan_dic = {'plan_name': plan_name, 'scan_steps': sequence_save_list}
        with open(os.path.join(plan_dir, file), "w") as f:
            yaml.safe_dump(plan_dic, f)

    @staticmethod
    def load_processing_plan(plan_dir, plan_name):
        # try:
            if not os.path.exists(plan_dir):
                os.mkdir(plan_dir)
                return

            with open(os.path.join(plan_dir, plan_name), "r") as f:
                plan_dict = yaml.safe_load(f)
                sequence = ProcessingSequence()
                step_dict = sequence.step_object_dict
                for step in plan_dict["scan_steps"]:
                    step_object = step_dict[step["processing_name"]][0]()
                    for param_key, param_value in step.items():
                        if param_key not in ["processing_name", "processing_input_number"]:
                            if step_object.get_params()[param_key]["type"] == "enum":
                                enum_type = type(step_object.get_params()[param_key]["value"])
                                for attr in enum_type:
                                    if attr.value == param_value:
                                        step_object.set_param(param_key, attr)
                                        break
                            else:
                                step_object.set_param(param_key, param_value)
                    sequence.add_step_in_data(step["processing_name"], step_object, step["processing_input_number"])
                return sequence
        # except (OSError, KeyError):
        #    return None
