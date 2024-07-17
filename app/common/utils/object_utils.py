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
