class ArrayOfChats(object):

    def __init__(self):
        self.listofarrays = {}
    
    def get_list_of_chats(self):
        return self.listofarrays
    
    def get_chat(self, i):
        return self.listofarrays.get(i, [])

    def add_message(self, i, s):
        arr = self.get_chat(i)
        arr.append(s)
        self.listofarrays.update({i: arr}) 
        self.get_chat(i)

    def delete_array(self, i):
        self.listofarrays.pop(i)
        self.get_list_of_chats()

    def delete_listofarrays(self):
        self.listofarrays.clear()
