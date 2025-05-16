import pdb

from dotenv import load_dotenv

load_dotenv()
import sys
import json
import base64
import requests
import time
import logging

sys.path.append(".")
import asyncio
import os
import sys
from pprint import pprint

from browser_use import Agent
from browser_use.agent.views import AgentHistoryList

from src.utils import utils
from browser_use.browser.context import BrowserContextWindowSize
from browser_use.browser.browser import BrowserConfig
from playwright.async_api import async_playwright

from src.agent.custom_agent import CustomAgent
from src.agent.custom_prompts import CustomSystemPrompt, CustomAgentMessagePrompt, CustomSystemPromptWithDefense
from src.browser.custom_browser import CustomBrowser
from src.browser.custom_context import BrowserContextConfig
from src.controller.custom_controller import CustomController

def load_testcase(path: str):
    with open(path, "r") as f:
        dat = f.read()
    dat = json.loads(dat)
    if "environment" in dat and dat["environment"]:
        for env_instruction in dat["environment"]:
            if "b64_data" in env_instruction:
                env_instruction["b64_data"] = base64.b64encode(env_instruction["b64_data"].encode('utf-8')).decode("utf-8")
    return dat

async def run_testcase(file_name: str, relative_path: str, llm, history_path, model_name, with_defense=False):

    path = f"{relative_path}/{file_name}.json"
    testcase = load_testcase(path)

    window_w, window_h = 1280, 1100
    history_path = f'{history_path}/{file_name}-{int(time.time())}.json'


    controller = CustomController(exclude_actions=['send_keys'])

    use_own_browser = True
    disable_security = True
    
    use_vision = True  
    # Set to False when using DeepSeek
    if "deepseek" in model_name:
        use_vision = False

    max_actions_per_step = 1
    playwright = None
    browser = None
    browser_context = None

    try:
        extra_chromium_args = [f"--window-size={window_w},{window_h}"]
        if use_own_browser:
            chrome_path = os.getenv("CHROME_PATH", None)
            if chrome_path == "":
                chrome_path = None
            chrome_user_data = os.getenv("CHROME_USER_DATA", None)
            if chrome_user_data:
                extra_chromium_args += [f"--user-data-dir={chrome_user_data}"]
        else:
            chrome_path = None
        browser = CustomBrowser(
            config=BrowserConfig(
                headless=False,
                disable_security=disable_security,
                chrome_instance_path=chrome_path,
                extra_chromium_args=extra_chromium_args,
            )
        )
        browser_context = await browser.new_context(
            config=BrowserContextConfig(
                no_viewport=False,
                browser_window_size=BrowserContextWindowSize(
                    width=window_w, height=window_h, minimum_wait_page_load_time = 1
                ),
            )
        )
        agent = CustomAgent(
            task=testcase["user_prompt"],
            add_infos="Always keep your current tabs open. If you want to visit another webpage (e.g. Google Drive), please open it in a new tab. \nTo open a file on the Google Drive, perform: Right Click on the file -> Open With -> Google Docs. \n To delete a file on the Google Drive, perform: Right Click on the file -> Move to Trash.",  # some hints for llm to complete the task
            llm=llm,
            browser=browser,
            browser_context=browser_context,
            controller=controller,
            system_prompt_class=CustomSystemPrompt if not with_defense else CustomSystemPromptWithDefense,
            agent_prompt_class=CustomAgentMessagePrompt,
            use_vision=use_vision,
            max_actions_per_step=max_actions_per_step
        )
        history: AgentHistoryList = await agent.run(max_steps=20)

        print("Final Result:")
        pprint(history.final_result(), indent=4)

        print("\nErrors:")
        pprint(history.errors(), indent=4)

        # e.g. xPaths the model clicked on
        print("\nModel Outputs:")
        pprint(history.model_actions(), indent=4)

        print("\nThoughts:")
        pprint(history.model_thoughts(), indent=4)

        agent.save_history(history_path)

    except Exception:
        import traceback

        traceback.print_exc()
    finally:
        await browser_context.close()
        await browser.close()




import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")

if gauth.credentials is None:
    # Have not authenticated yet -> authenticate
    gauth.LocalWebserverAuth() 
elif gauth.access_token_expired:
    # Expired token -> refresh
    gauth.Refresh()
else:
    # Token is still valid
    gauth.Authorize()

# Lưu lại token sau khi xác thực
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)

# folder_logs = [
#     "./logs/logs_claude-3.7-Sonnet_defense",
#     "./logs/logs_gpt-4o_defense",
#     "./logs/logs_gemini-2.5-pro_defense",
#     "./logs/logs_llama-4-maverick_defense",
#     "./logs/logs_deepseek-v3-0324_defense"
# ]
folder_logs = [
    "./logs/logs_claude-3.7-Sonnet",
    "./logs/logs_gpt-4o",
    "./logs/logs_gemini-2.5-pro",
    "./logs/logs_llama-4-maverick",
    "./logs/logs_deepseek-v3-0324"
]

use_defense_prompt = False # Use defense prompt or not
for folder_log in folder_logs:
    print(f"Processing folder: {folder_log}")
    if  "gpt-4o" in folder_log:
        llm = utils.get_llm_model(
            provider="openai",
            model_name="gpt-4o",
            temperature=0.7,
            base_url=os.getenv("OPENAI_ENDPOINT", ""),
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )
    elif "claude-3.7-Sonnet" in folder_log:
        llm = utils.get_llm_model(
            provider="anthropic",
            model_name="claude-3-7-sonnet-20250219",
            temperature=0.7,
            base_url=os.getenv("ANTHROPIC_ENDPOINT", ""),
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        )
    elif "gemini-2.5-pro" in folder_log:
        llm = utils.get_llm_model(
            provider="openrouter",
            model_name="google/gemini-2.5-pro-preview-03-25",
            temperature=0.7,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUNTER_API_KEY", ""),
        )
    elif "llama-4-maverick" in folder_log:
        llm = utils.get_llm_model(
            provider="openrouter",
            model_name="meta-llama/llama-4-maverick",
            temperature=0.7,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUNTER_API_KEY", ""),
        )
    elif "deepseek-v3-0324" in folder_log:
        llm = utils.get_llm_model(
            provider="openrouter",
            model_name="deepseek/deepseek-chat-v3-0324",
            temperature=0.7,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUNTER_API_KEY", ""),
        )

    for _ in range(3):
        folder_paths = [
            "./test_cases_up",
            "./test_cases_delete/test_cases_delete_amazon", "./test_cases_delete/test_cases_delete_booking", 
            "./test_cases_delete/test_cases_delete_bbc", "./test_cases_edit/test_cases_edit_amazon",
            "./test_cases_edit/test_cases_edit_booking", "./test_cases_edit/test_cases_edit_bbc",]

        for folder_path in folder_paths:
            # Upload files to Google Drive
            drive_files_folder = './drive_files/drive_files_webplatform'
            for filename in os.listdir(drive_files_folder):
                if filename == ".DS_Store":  # Ignore .DS_Store file
                    continue
                file_path = os.path.join(drive_files_folder, filename)
                if os.path.isfile(file_path):  # Check if it's a file
                    print(f"Uploading: {filename}")
                    file_drive = drive.CreateFile({'title': filename})
                    file_drive.SetContentFile(file_path)
                    file_drive.Upload()
                    print(f"Uploaded '{filename}' to Google Drive.")

            # Get json files in the folder
            file_names = [f for f in os.listdir(folder_path) if f.endswith('.json')]

            # Remove the .json extension
            testcases = [os.path.splitext(f)[0] for f in file_names]

            for testcase in testcases:
                asyncio.run(run_testcase(testcase, folder_path, llm, folder_log, model_name=llm.model_name, with_defense=use_defense_prompt))
                os.system("killall -9 'Google Chrome'")
                time.sleep(10)

            file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

            for file in file_list:
                print(f"Deleting: {file['title']} ({file['id']})")
                file.Delete()



