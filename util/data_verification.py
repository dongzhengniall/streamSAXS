class DataVerification(object):
    @staticmethod
    def int(value):
        try:
            value = int(value)
            return value
        except Exception as e:
            return None

    @staticmethod
    def float(value):
        try:
            value = float(value)
            return value
        except Exception as e:
            return None

    @staticmethod
    def str(value):
        try:
            value = str(value)
            return value
        except Exception as e:
            return None

    @staticmethod
    def tuple(value):
        try:
            value = value.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("{", "").replace(
                "}", "").replace("（", "").replace("）", "")
            min = float(value[:value.find(",")])
            max = float(value[value.find(",") + 1:])
            value = (min, max)
            return value
        except Exception as e:
            return None

    @staticmethod
    def tuple_float(value):
        value=str(value)
        try:
            value = value.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("{", "").replace(
                "}", "").replace("（", "").replace("）", "")
            min = float(value[:value.find(",")])
            max = float(value[value.find(",") + 1:])
            value = (min, max)
            return value
        except Exception as e:
            return None

    @staticmethod
    def tuple_int(value):
        value = str(value)
        try:
            value = value.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("{", "").replace(
                "}", "").replace("（", "").replace("）", "")
            min = int(value[:value.find(",")])
            max = int(value[value.find(",") + 1:])
            value = (min, max)
            return value
        except Exception as e:
            return None

    @staticmethod
    def enum(value):
        try:
            return value
        except Exception as e:
            return None

    @staticmethod
    def bool(value):
        try:
            return value
        except Exception as e:
            return None

    @staticmethod
    def io(value):
        try:
            return value
        except Exception as e:
            return None