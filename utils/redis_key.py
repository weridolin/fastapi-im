
class RedisKey:

    @staticmethod
    def user_info_key(user_id:int):
        return f"im.user.info.{user_id}"
    
