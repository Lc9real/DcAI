import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler
import warnings

fastpic = True

if fastpic:
    global pipe
    pipe = StableDiffusionPipeline.from_single_file(
            "C:\sdwebui\Stable2\stable-diffusion-webui\models\Stable-diffusion\SSD-1B.safetensors",
            torch_dtype=torch.float16,
        ).to("cuda")
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
    pipe.safety_checker = None


def generate_image(prompt):

    if fastpic == False:
        global pipe
        pipe = StableDiffusionPipeline.from_single_file(
            "C:\sdwebui\Stable2\stable-diffusion-webui\models\Stable-diffusion\epicrealism_pureEvolutionV3.safetensors",
            torch_dtype=torch.float16,
        ).to("cuda")
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
        pipe.safety_checker = None


    with autocast("cuda"):
        image = pipe(prompt , num_inference_steps=25, guidance_scale=3, negative_prompt="lowres, text, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, username, watermark, signature, deformed face, unrealistic face, distorted face")["images"]
        image = image[0]
    file_name:str = prompt.replace(" ", "_")[:40]
    image.save("images/" + file_name + ".png")
    return "C:/Users/lukac/PycharmProjects/DcAIV1.2/images/" + file_name + ".png"


generate_image("test")