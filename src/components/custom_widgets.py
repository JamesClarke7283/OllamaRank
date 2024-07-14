import customtkinter as ctk

class CTkListbox(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.items = []

    def insert(self, index, item):
        if index == "end":
            index = len(self.items)
        
        label = ctk.CTkLabel(self, text=item, anchor="w")
        label.pack(fill="x", padx=5, pady=2)
        self.items.insert(index, (item, label))

    def delete(self, index):
        if isinstance(index, int) and 0 <= index < len(self.items):
            item, label = self.items.pop(index)
            label.destroy()

    def get(self, index):
        if isinstance(index, int) and 0 <= index < len(self.items):
            return self.items[index][0]
        return None

    def size(self):
        return len(self.items)