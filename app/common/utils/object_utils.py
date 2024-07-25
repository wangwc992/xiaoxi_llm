class ObjectFormatter:
    @staticmethod
    def format_object(obj):
        """
      将对象的所有属性值取出，用 "——" 拼接成字符串。

      :param obj: 需要格式化的对象
      :return: 拼接好的字符串
      """
        # 获取对象所有的属性名和值
        attributes = [getattr(obj, attr) for attr in dir(obj) if
                      not callable(getattr(obj, attr)) and not attr.startswith("__")]

        # 过滤掉 None 值
        attributes = [str(attr) for attr in attributes if attr is not None]

        # 使用 "——" 拼接
        return "——".join(attributes)

    @staticmethod
    def format_objects(objects):
        """
      格式化一个对象列表的信息。

      :param objects: 对象列表
      :return: 每个对象拼接好的字符串列表
      """
        return [ObjectFormatter.format_object(obj) for obj in objects]

    @staticmethod
    def format_dict(dict: dict) -> str:
        """
      格式化一个字典的信息。值 使用 "——" 拼接成字符串。

        :param dict: 字典
        :return: 拼接好的字符串
        """
        return "—".join([f"{key}: {value}" for key, value in dict.items()])

    @staticmethod
    def format_dicts(dicts: list) -> list[str]:
        """
      格式化一个字典列表的信息。

      :param dicts: 字典列表
      :return: 每个字典拼接好的字符串列表
      """
        return [ObjectFormatter.format_dict(dict) for dict in dicts]

    @staticmethod
    def dict_to_object(dict: dict, obj_class):
        """
      将字典转换成对象。

      :param dict: 字典
      :param obj_class: 对象类
      :return: 对象
      """
        obj = obj_class()
        for key, value in dict.items():
            setattr(obj, key, value)
        return obj

    @staticmethod
    def attribute_concatenation(key_name_list, zn_school_department_project_dict_list):
        """
        根据提供的键名列表和字典列表，生成包含格式化输出和指令的字典列表。

        此方法用于将专业信息的各个属性按照特定格式组合成字符串，并为每个属性生成一个指令字符串。
        指令字符串由属性名组成，用于指示哪些属性被包含在输出中。

        :param key_name_list: 包含键名和对应显示名称的字典列表，例如 [{'所属院系': 'department'}]。
        :param zn_school_department_project_dict_list: 包含专业信息的字典列表，每个字典代表一个专业的信息。
        :return: 一个字典列表，每个字典包含两个键：'output' 和 'instruction'。
                 'output' 键对应的值是格式化后的专业信息字符串，'instruction' 键对应的值是包含所有包含属性名的字符串。
        """
        dict_list = []
        for zn_school_department_project_dict in zn_school_department_project_dict_list:
            output = ""
            instruction = ""
            for key_name in key_name_list:
                key = list(key_name.keys())[0]
                value = zn_school_department_project_dict[key_name[key]]
                if value:
                    instruction += f"{key} "
                    output += f"{key}：{value}、 "
            dict = {"output": output.rstrip("、 "), "instruction": instruction.rstrip()}
            dict_list.append(dict)
        return dict_list

    #写一个整理key和value的方法，传入key_name_list,