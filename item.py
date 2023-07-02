class Item:
    def __init__(self, item_data):
        
        item_data = item_data.splitlines()

        for s in item_data:
            s.strip()

        parsed_item_data = [[]]
        parsed_item_data.extend([e] for e in item_data if e=="--------" or parsed_item_data[-1].append(e))
        
        self.item_type = item_data[0].partition(': ')[2]
        self.rarity = item_data[1].partition(': ')[2]
        self.name = item_data[2]
        self.base = item_data[3]

        self.defences = parsed_item_data[1][1:]
        self.requirements = parsed_item_data[2][2:]
        self.sockets = parsed_item_data[3][1:]
        self.item_level = parsed_item_data[4][1:]
        self.modifiers = parsed_item_data[5][1:]

    def is_unique(self):
        return self.rarity == "Unique"