import time

class MapItem(object):
    value = ''
    type = -1 # 0 访问刷新   1 固定时常   2 修改刷新     3 访问次数    -1 不过期
    live_time = 0
    add_time = 0
    def __init__(self, value, type, live_time):
        self.value = value
        self.live_time = live_time
        self.type = type
        if self.type == 3:
            self.add_time = 0
        else:
            self.add_time = int(round(time.time()))
        
    def is_expried(self):
        res = False
        if self.type == 0 or self.type == 1 or self.type == 2:
            res = (self.add_time + self.live_time) >= int(round(time.time()))
        elif self.type == 3:
            res = self.add_time <= self.live_time
        elif self.type == -1:
            res = True
        

        if res:
            if self.type == 0:
                self.add_time = int(round(time.time()))
            elif self.type == 3:
                self.add_time = self.add_time + 1
        else:
            self.value = None

        return self.value
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

    def change_value(self, key, value):
        self.kv_map[key].value = value
        if self.kv_map[key].type == 2:
            self.kv_map[key].add_time = int(round(time.time()))
    def get_value(self, key):
        if key in self.kv_map:
            res = self.kv_map[key].is_expried()
            if res is not None:
                return res
            else:
                self.kv_map.pop(key)
        return None

