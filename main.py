from datetime import datetime
import re
import discord
from discord import app_commands
from llama_cpp import Llama
from llm_memory import Memory_System
import llm_prompt
#import tool_SD
import os

#set variables

try:
    model_name = open("./Model/Model_Name.txt", "r").readlines()[0]
except IndexError as e:
    raise IndexError("Model Name not Specified")



model_path = f"./Model/{model_name}"

if not os.path.exists(model_path):
    raise ValueError(f"Model does not exist check if model is in ./Model or if the name is right")
temperature = 0.4
n_gpu_layer = 100
n_batch = 40
max_tokens = 10000
Debug = True



memory = Memory_System("SIA")

# load model


llm = Llama(
    model_path=model_path,
    temperature=temperature,
    n_gpu_layers=n_gpu_layer,
    n_batch=n_batch,
    max_tokens=max_tokens,
    top_p=1,
    n_ctx=max_tokens,
    prompt=llm_prompt.generate_prompt(),
    verbose=False,
)



def check_pattern(pattern:str, text:str):
    matches = re.findall(pattern, text)
    if matches and "```" not in text:
        text = re.sub(pattern, '', text)
    else:
        matches = []
    return {"text": text, "matches": matches}

def call_Model(inp:str, channel_name:str, time, user_name="Unknown") -> str:
    short_mem, current_mem = memory.load_Memory(channel_name)
    prompt = llm_prompt.generate_prompt().format(user_name=user_name, input=inp, short_memory=short_mem, channel_name=channel_name, timestamp=time, current_memory=current_mem)
    print(prompt)
    output = llm(prompt, max_tokens=20000, stop=[";"])
    print(output)
    print(output["choices"][0]["text"])
    return output["choices"][0]["text"]



async def send_message(message, user_message, is_private, username:str, bot):
    user_timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    mark_pattern = r'\<@(.+?)\>'
    temp_d = check_pattern(mark_pattern, user_message)
    print(user_message)
    mark_matches = temp_d["matches"]
    for match in mark_matches:
        print(match)

    if "<@1165020606044049491>" in user_message:
        user_message = user_message.replace("<@1165020606044049491>", "@SIA")
        async with message.channel.typing():



            response = call_Model(user_message, message.channel, user_timestamp, username)
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")



            channel_pattern = r'\[(.*?)\]'
            picture_pattern = r'\{(.+?)\}'



            temp_d = check_pattern(channel_pattern, response)
            response = temp_d["text"]
            channel_matches = temp_d["matches"]


            temp_d = check_pattern(picture_pattern, response)
            response = temp_d["text"]
            image_matches = temp_d["matches"]




            if image_matches:
                image_files = []
                for match in image_matches:
                    path = tool_SD.generate_image(match)
                    response = response.replace(f'{{{match}}}', '')
                    image_files.append(discord.File(path))
                # memory
                images = ""
                for thing in image_matches:
                    images = images + " {" + thing + "}"

            if channel_matches:
                channel = discord.utils.get(message.guild.channels, name=channel_matches[0])
                channel_id = channel.id
                if image_matches:
                    if image_files:
                        if response:
                            await bot.get_channel(channel_id).send(response, files=image_files)
                            memory.add_Memory("SIA", response + images, channel_matches[0], timestamp)
                        else:
                            await bot.get_channel(channel_id).send(" ", files=image_files)
                            memory.add_Memory("SIA", images, channel_matches[0], timestamp)
                else:
                    await message.author.send(response) if is_private else bot.get_channel(channel_id).send(response)
            else:
                if image_matches:
                    if image_files:
                        if response:
                            await message.channel.send(response, files=image_files)
                            memory.add_Memory("SIA", response + images, message.channel, timestamp)
                        else:
                            await message.channel.send(" ", files=image_files)
                            memory.add_Memory("SIA", images, message.channel, timestamp)
                    else:
                        await message.channel.send(response)
                        memory.add_Memory("SIA", response + "\n'''Couldn't Send Image'''", message.channel, timestamp)
                else:
                    await message.channel.send(response)
                    memory.add_Memory("SIA", response + "\n'''Couldn't Send Image'''", message.channel, timestamp)
    memory.add_Memory(message.author, message.content, message.channel, user_timestamp)




def run_discord_bot():
    TOKEN = 'MTE2NTAyMDYwNjA0NDA0OTQ5MQ.GmEsyI.iXcRL5CyMprK6Lzu3bxS4ExPQYUxkWv6RgE_0k'
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    @client.event
    async def on_ready():
        await tree.sync()
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):

        if message.author == client.user:
            return


        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        await send_message(message, user_message, is_private=False, username=username, bot=client)

    @tree.command(name="clear_memory", description="Clears SIA's Memory")
    async def clear_memory(ctx):
        memory.clear_Memory()
        await ctx.response.send_message("Cleared Memory")

    @tree.command(name="send", description="send message in channel")
    async def send_a_message(ctx, name:str):
        channel = discord.utils.get(ctx.guild.channels, name=name)
        channel_id = channel.id
        await client.get_channel(channel_id).send("Hello ")
        await ctx.response.send_message("Ok")



    client.run(TOKEN)

run_discord_bot()