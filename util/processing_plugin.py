import os
import sys
import importlib
import inspect


# 导入模块
def import_module_from_spec(module_spec):
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


# 找出模块里所有的类名
def get_classes(arg):
    classes = []
    clsmembers = inspect.getmembers(arg, inspect.isclass)
    for (name, _) in clsmembers:
        classes.append(name)
    return classes


def get_file_name_from_path(file_path, file_type):
    all_file_name_list = os.listdir(file_path)
    file_name_list = [file_name[:-len(file_type)] for file_name in all_file_name_list if file_name[-len(file_type):] == file_type]
    file_path_list = [file_path + "\\" + file_name+file_type for file_name in file_name_list]
    return {"file_name_list": file_name_list, "file_path_list": file_path_list}


def get_classes_from_path(file_path, file_type):
    classes = []
    file_list = get_file_name_from_path(file_path, file_type)
    file_name_list = file_list["file_name_list"]
    file_path_list = file_list["file_path_list"]
    for i in range(len(file_name_list)):
        sys.path.append(file_path_list[i])
        spec = importlib.util.spec_from_file_location(file_name_list[i], file_path_list[i])
        module = import_module_from_spec(spec)
        class_list = get_classes(module)
        for j in range(len(class_list)):
            class_list[j] = getattr(module, class_list[j])
        classes = classes + class_list
    return classes


def filter_classes_by_function(classes, has_attribute):
    filter_classes = []
    for class_object in classes:
        if hasattr(class_object, has_attribute):
            if class_object.function_text:
                filter_classes.append(class_object)

    return filter_classes
