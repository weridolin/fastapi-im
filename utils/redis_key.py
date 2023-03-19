
class RedisKey:

    @staticmethod
    def user_info_key(user_id:int):
        return f"im.user.info.{user_id}"
    

    @staticmethod
    def user_msg_channel(user_id:int):
        ## 用户未读的消息信箱（1对1）
        return f"im.user.msg.{user_id}"

    @staticmethod
    def user_group_msg_channel(user_id:int,group_id:int):
        ## 用户未读的消息信箱（1对1）
        return f"im.user.msg.{user_id}.{group_id}"
    
    @staticmethod
    def user_msg_channel_groups_name(user_id:int,type:str):
        ## 用户消息信道消费者组名称
        return f"{user_id}.{type}"