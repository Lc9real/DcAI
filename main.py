from datetime import datetime
import re
import discord
from discord import app_commands
from llama_cpp import Llama
from llm_memory import Memory_System
import llm_prompt
import tool_SD
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
max_tokens = 6900
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




def call_Model(inp:str, channel_name:str, time, user_name="Unknown") -> str:
    short_mem, current_mem = memory.load_Memory(channel_name)
    prompt = llm_prompt.generate_prompt().format(user_name=user_name, input=inp, short_memory=short_mem, channel_name=channel_name, timestamp=time, current_memory=current_mem)
    output = llm(prompt, max_tokens=20000, stop=[";"])
    print(output["choices"][0]["text"])
    return output["choices"][0]["text"]



async def send_message(message, user_message, is_private, username:str, bot):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    if "<@1165020606044049491>" in user_message:
        user_message = user_message.replace("<@1165020606044049491>", "@SIA")
        memory.add_Memory(message.author, user_message, message.channel, timestamp)
        async with message.channel.typing():


            response = call_Model(user_message, message.channel, timestamp, username)
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")


            channel_pattern = r'\[(.*?)\]'
            picture_pattern = r'\{(.+?)\}'

            channel_matches = re.findall(channel_pattern, response)
            if channel_matches and "```" not in response:
                response = re.sub(channel_pattern, '', response)
                channel = discord.utils.get(message.guild.channels, name=channel_matches[0])
                channel_id = channel.id

            matches = re.findall(picture_pattern, response)
            if matches and "```" not in response:
                image_files = []

                for match in matches:
                    path = tool_SD.generate_image(match)
                    response = response.replace(f'{{{match}}}', '')
                    image_files.append(discord.File(path))

                if "```" in response:
                    channel_matches = None
                    image_files = None

                #memory
                images = ""
                for thing in matches:
                    images = images + " {" + thing + "}"

                #send message
                if image_files:
                    if response:
                        if channel_matches:

                            await bot.get_channel(channel_id).send(response, files=image_files)
                            memory.add_Memory("SIA", response + images, channel_matches[0], timestamp)
                        else:
                            await message.channel.send(response, files=image_files)
                            memory.add_Memory("SIA", response + images, message.channel, timestamp)
                    else:
                        if channel_matches:
                            await bot.get_channel(channel_id).send(" ", files=image_files)
                            memory.add_Memory("SIA", images, channel_matches[0], timestamp)
                        else:
                            await message.channel.send(" ",files=image_files)
                            memory.add_Memory("SIA", images, message.channel, timestamp)
            else:
                if channel_matches:
                    await message.author.send(response) if is_private else bot.get_channel(channel_id).send(response)
                else:
                    memory.add_Memory("SIA", response, message.channel, timestamp)

                    await message.author.send(response) if is_private else await message.channel.send(response)
    else:
        memory.add_Memory(message.author, message.content, message.channel, timestamp)




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