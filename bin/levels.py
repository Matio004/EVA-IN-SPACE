

# LevelData
class LevelData:
    def __init__(self, level_number: int, kills: int, unlocked=None):
        self.level_number = level_number
        self.kills = kills
        if unlocked is None:
            self.unlocked = True if self.level_number == 1 else False
        else:
            self.unlocked = unlocked

    def __repr__(self):
        return f'Level {self.level_number}(kills: {self.kills})'

    def __iter__(self):
        return iter([self.level_number, self.kills, self.unlocked])


# Create levels
def create_levels(levels_count: int = 1):
    levels_list = []
    for i in range(1, levels_count+1):
        levels_list.append(LevelData(level_number=i, kills=50 * i))
    return levels_list


def list_to_level(_list):
    return LevelData(_list[0], _list[1], _list[2])
