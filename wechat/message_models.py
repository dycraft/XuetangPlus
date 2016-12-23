class MessageModel():
    def create_remind_model(self, open_id, hw_num, info_num, time):
        model = {
            "touser": open_id,
            "template_id": "9m7L5-CaYcso5LVrT38NBcRNZ60BG_vIxXM1WKZwGCw",
            "data": {
                "first": {
                    "value": "",
                    "color": "#173177"
                },
                "keyword1": {
                    "value": str(hw_num),
                    "color": "#173177"
                },
                "keyword2": {
                    "value": str(info_num),
                    "color": "#173177"
                },
                "keyword3": {
                    "value": time,
                    "color": "#173177"
                },
                "remark": {
                    "value": "我服",
                    "color": "#173177"
                }
            }
        }

        return model