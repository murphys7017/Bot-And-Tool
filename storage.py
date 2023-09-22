import time

class MapItem(object):
    value = ''
    type = -1 # 0 访问刷新   1 固定时常   2 修改刷新     3 访问次数    -1 不过期
    live_time = 0
    add_time = 0
    def __init__(self, key, value, type, live_time):
        self.key = key
        self.value = value
        self.live_time = live_time
        self.type = type
        if self.type == 3:
            self.add_time = 0
        else:
            self.add_time = int(round(time.time())*1000)
        
    def is_expried(self):
        if self.type == 0 or self.type == 1 or self.type == 2:
            return self.add_time + self.live_time >= int(round(time.time())*1000)
        elif self.type == 3:
            return self.add_time >= self.live_time
        elif self.type == -1:
            return False
class Storage(object):
    # 不过期表
    kv_map = {}
    def check_map(self):
        temp_map = self.kv_map
        for k,v in temp_map.items():
            if v.is_expried():
                self.kv_map.pop(k)
        self.map_list = temp_map
    def add_map(self, key, value, type, live_time):
        self.kv_map[key] = MapItem(value, type, live_time)
        return
    
    def get_value(self, key):
        res = self.kv_map[key]
        if res.type == 0:
            res.add_time = int(round(time.time())*1000)
            self.kv_map[key] = res
        return res.value