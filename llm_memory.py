import os

class Memory_System():
    def __init__(self, MemoryKey:str):
        self.memory_key = MemoryKey
        if not os.path.exists(f"./Memory/{self.memory_key}"):
            os.makedirs(f"./Memory/{self.memory_key}")


    def load_Memory(self, current_channel:str) -> str:
        allfiles = os.listdir(f'./Memory/{self.memory_key}')
        content = ""
        current_channel_text = ""
        for file in allfiles:
            f = open(f"./Memory/{self.memory_key}/{file}", "r", encoding="utf-8")

            if str(file[:-7]) == str(current_channel):

                current_channel_text = f"\n###{file[:-7]}###\n\n" + f.read()
                f.close()
            else:
                content = content + f"\n###{file[:-7]}###\n\n" + f.read()
                f.close()

        content = content

        return content, current_channel_text


    def add_Memory(self, username:str, inp:str, channel, time):
        f = open(f"./Memory/{self.memory_key}/{channel}.memory", "a", encoding="utf-8")
        if inp:
            f.write(f"{username}: {inp};({time})\n")
        f.close()

    def clear_Memory(self):
        os.remove(f"./Memory/{self.memory_key}")
        os.makedirs(f"./Memory/{self.memory_key}")



