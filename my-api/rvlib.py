import sys
import json
import math
import torch
import subprocess
import os
import transformers
from transformers import AutoConfig
from langchain_community.document_loaders import PyPDFLoader
import time
# from llama_attn_replace import replace_llama_attn

class TextGenerationPipeline:
    def __init__(self, device, model_name, tokenizer_name):
        SEQ_LEN = 32768
        self.device = device               
        self.config, self.orig_ctx_len = self.setup_model_config(model_name,SEQ_LEN)
       
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(
        tokenizer_name,
        model_max_length=SEQ_LEN if SEQ_LEN > self.orig_ctx_len else self.orig_ctx_len,
        padding_side="right",
        use_fast=False,
        )

        self.model = transformers.AutoModelForCausalLM.from_pretrained(
        model_name,
        config=self.config,
        torch_dtype=torch.bfloat16,
        offload_folder="offloaded_weights_folder",
        device_map="auto"
        )
        
        self.model.resize_token_embeddings(32001)
        self.model.eval()
        if torch.__version__ >= "2"  and sys.platform != "win32":
            self.model = torch.compile(self.model)
        
        
        
    def build_generator(self,
    model, tokenizer, temperature=0.7, top_p=0.7, top_k=50, max_new_tokens=1024, min_new_tokens=64, repetition_penalty=1.13
):
        def response(prompt):
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)        
            output = model.generate(
                **inputs,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_new_tokens=max_new_tokens,
                min_new_tokens=min_new_tokens,
                repetition_penalty=repetition_penalty,
                do_sample=True,
            )        
            out = tokenizer.decode(output[0], skip_special_tokens=True)
            try:
                out = out.split(prompt.lstrip("<s>"))[1].strip()
            except:
                out = []

            return out

        return response
    

    def setup_model_config(self,model_name, seq_len):
        """
        Create and set the model configuration, including the RoPE scaling 
        factor, and return the original maximum position embedding length.

        Parameters:
            model_name (str): The name of the pre-trained model.
            seq_len (int): The target sequence length.

        Returns:
            orig_ctx_len (int): The original maximum position embedding length.
        """
        config = AutoConfig.from_pretrained(model_name)

        orig_rope_scaling = getattr(config, "rope_scaling", None)
        if orig_rope_scaling is None:
            orig_rope_scaling = {"factor": 1}

        orig_rope_scaling_factor = orig_rope_scaling["factor"] if "factor" in orig_rope_scaling.keys() else 1
        orig_ctx_len = getattr(config, "max_position_embeddings", None)

        if orig_ctx_len:
            orig_ctx_len *= orig_rope_scaling_factor
            if seq_len > orig_ctx_len:
                scaling_factor = float(math.ceil(seq_len / orig_ctx_len))
                config.rope_scaling = {"type": "linear", "factor": scaling_factor}
                print(f'rope scaling factor {scaling_factor}')

        return config, orig_ctx_len

class PromptGenerator(TextGenerationPipeline):
    DEFAULT_MODEL_NAME = 'GitBag/Reviewer2_Mp'
    DEFAULT_TOKENIZER_NAME = 'GitBag/Reviewer2_Mp'    
    def __init__(self, device: str = None, model_name: str = DEFAULT_MODEL_NAME, tokenizer_name: str =DEFAULT_TOKENIZER_NAME):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"        
        super().__init__(device=device, model_name=model_name, tokenizer_name=tokenizer_name)

    def generate_prompt(self, paper_content, version="default"):
        print(f"Generating prompt with version: {version}")
        print(f"Paper Content: {paper_content}")
        if version == "default":
            prompt_Llama_2 = (
            "[INST] <<SYS>>\n"
            "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n"
            "If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n"
            "<</SYS>>\nRead the following paper carefully:\n{paper_content}\n\n\n"
            "Your task is to construct a list of questions about the paper for the reviewer to answer.\n"
            "\nThe reviewer should answer in the following format:\n{format}\n"
            "[/INST]"
            )
            prompt_dict = {
            'paper_content': paper_content,
            'format': '\n'.join(['Summary Of The Paper', 'Strengths And Weaknesses'])
            }
            prompt = prompt_Llama_2.format_map(prompt_dict)        
            prompt_generator = self.build_generator(self.model, self.tokenizer)
            gen_prompt = prompt_generator(prompt)
        else:
            prompt_Llama_2 = (
            "[INST] <<SYS>>\nYou are a helpful, respectful, and honest assistant. Provide detailed, constructive "
            "questions focusing on comprehensive evaluation of the paper. Ensure your questions adhere to safety "
            "and ethical guidelines. Your responses must exclude any harmful, unethical, racist, sexist, toxic, "
            "dangerous, or illegal content. Ensure that your responses are socially unbiased and positive in nature.\n"
            "If a question posed by the paper does not make sense, or is not factually coherent, explain why instead "
            "of providing incorrect information. If you are uncertain about any details, clarify your uncertainty rather "
            "than disseminating false information.\n<</SYS>>\nRead the following paper carefully:\n{paper_content}\n"
            "Your task is to construct a list of questions about the paper for an LLM reviewer to answer and provide "
            "detailed feedback and suggestions for improving the paper. These questions should encourage the reviewer to "
            "critically assess both the strengths and weaknesses of the work, as well as suggest specific areas for improvement.\n[/INST]"
            )
            prompt_dict = {
            'paper_content': paper_content,
            }
            prompt = prompt_Llama_2.format_map(prompt_dict)        
            prompt_generator = self.build_generator(self.model, self.tokenizer)
            gen_prompt = prompt_generator(prompt)

        questions_start = gen_prompt.find("1.")
        questions = gen_prompt[questions_start:] if questions_start != -1 else "No questions generated."

        final_prompt = "Here are some suggested questions based on the paper provided for review. You may adjust them as needed:\n\n" + questions
        
        return final_prompt

class ReviewGenerator(TextGenerationPipeline):
    DEFAULT_MODEL_NAME = 'GitBag/Reviewer2_Mr'
    DEFAULT_TOKENIZER_NAME = 'GitBag/Reviewer2_Mr'    
    def __init__(self, device: str = None, model_name: str = DEFAULT_MODEL_NAME, tokenizer_name: str =DEFAULT_TOKENIZER_NAME):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"        
        super().__init__(device=device, model_name=model_name, tokenizer_name=tokenizer_name)        

    def generate_review(self, paper_content, gen_prompt, version="default"):
        print(f"Generating review with version: {version}")
        if version == "default":
            prompt_Llama_2 = (
            "[INST] <<SYS>>\n"
            "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n"
            "If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n"
            "<</SYS>>\nRead the following paper carefully:\n{paper_content}\n\n\n"
            "Your task is to compose a high-quality review of the paper submitted to a top-tier conference.\n"
            "Your review should contain the answers to the following questions:\n{prompt_gen}\n"
            "\nWrite your review into following section:\n{format}\n"
            "[/INST]"
            )
            prompt_dict = {
            'paper_content': paper_content,
            'prompt_gen': gen_prompt,
            'format': '\n'.join(['Summary Of The Paper', 'Strengths And Weaknesses', 'Questions', 'Limitations'])
            }
            prompt = prompt_Llama_2.format_map(prompt_dict)
            review_generator = self.build_generator(self.model,self.tokenizer)
            gen_review = review_generator(prompt)
        else:
            prompt_Llama_2 = (
            "[INST] <<SYS>>\n"
            "You are a helpful, respectful, and honest assistant. Provide a detailed and constructive review, focusing on both strengths and areas for improvement. Ensure that your feedback includes specific suggestions for enhancing the paper. Avoid any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n"
            "If a question does not make sense, or is not factually coherent, explain why instead of answering incorrectly. If you are unsure about any detail, clarify that uncertainty rather than sharing inaccurate information.\n"
            "<</SYS>>\nRead the following paper carefully:\n{paper_content}\n\n\n"
            "Your task is to compose a high-quality review of the paper submitted to a top-tier conference.\n"
            "In your review, please address the following questions in a concise paragraph:\n{prompt_gen}\n"
            "Refer to question prompts. Include specific suggestions for how each weakness can be improved, mentioning particular sections of the paper where relevant"
            "\nWrite your detailed review in the following section:\n{format}\n"
            "[/INST]"
            )
            prompt_dict = {
            'paper_content': paper_content,
            'prompt_gen': gen_prompt,
            'format': '\n'.join([
                'Summary of the Paper and Key Points:',
                '\nMain Contributions and Technical Discussion',
                '\nContextual Relevance and Novelty',
                '\nStrengths of the Paper:',
                '\nWeaknesses and Areas for Improvement:',
                '\nQuestions'
                '\nConclusion and Final Recommendations'
            ])
            }
            prompt = prompt_Llama_2.format_map(prompt_dict)
            review_generator = self.build_generator(self.model,self.tokenizer)
            gen_review = review_generator(prompt)
        return gen_review

# ============Paper Content============
def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__} 执行时间: {end_time - start_time:.6f}秒")
        return result
    return wrapper

# Load the PDF file and return its text content
@timer_decorator
def load_pdf_file_pypdf(content_path):
    loader = PyPDFLoader(content_path)
    paper_content = ""
    pages = loader.load_and_split()
    for page in pages:
        paper_content += page.page_content
    paper_content=json.dumps(paper_content)
    return paper_content

def parse_pdf_to_json(pdf_path, json_save_dir):
    json_path = None

    java_command = ["java", "-Xmx16g", "-jar", "./science-parse-cli-assembly-2.0.3.jar", "PATH_TO_PDF", "-o", "JSON_SAVE_DIRECTORY"]

    java_command[4] = pdf_path
    java_command[6] = json_save_dir

    try:
        subprocess.run(java_command, check=True)
        json_path = os.path.join(json_save_dir, os.path.basename(pdf_path) + '.json')
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
    
    return json_path

# Example function call
# parse_pdf_to_json("/path/to/input.pdf", "/path/to/output/directory")
def parse_paper_content(json_path):
    with open(json_path, 'rb') as p:
        paper_data = json.load(p)
    
    paper_content = []
    paper_content.append('Title')
    paper_content.append(paper_data['metadata']['title'])
    paper_content.append('Abstract')
    paper_content.append(paper_data['metadata']['abstractText'])
            
    # use full paper
    for section in paper_data['metadata']['sections']:
        paper_content.append(section['heading'])
        paper_content.append(section['text'])
    for i in range(len(paper_content)):
        if paper_content[i] == None:
            paper_content[i] = 'N/A'
    paper_content = "\n".join(paper_content).encode("utf-8", "ignore").decode("utf-8").strip()
    return paper_content
    
def TestApi():
    # Hardcoded responses for the default version
    default_prompt = "Default Version Prompt: Summarize the main findings of the paper."
    default_review = "Default Version Review: The paper provides a concise overview of current AI trends."

    # Hardcoded responses for the detailed version
    detailed_prompt = "Detailed Version Prompt: Provide a detailed analysis of the paper's methodology and its implications in the field of AI."
    detailed_review = "Detailed Version Review: This paper extensively discusses advanced AI methodologies and their potential impact on future technologies, highlighting several areas for improvement and further research."

    return {
        "default": {
            "prompt": default_prompt,
            "review": default_review
        },
        "detailed": {
            "prompt": detailed_prompt,
            "review": detailed_review
        }
    }