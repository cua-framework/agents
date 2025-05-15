# Introduction

For Computer-Use Agents (CUAs), as we are only using Anthropic's Sonnet 3.5 and Sonnet 3.7 models, we use a modified computer environment adapted from Anthropic's Computer-Use QuickStart.

More specifically, we use the same exact Debian-based Virtual Machine (VM) as Anthropic (i.e. same apps, configurations, etc.), but with a few additional changes.

Notably, we added a FastAPI server in the VM, and exposed it through an additional port, so that we can send prompts and other instructions from outside the VM to the CUA located inside the VM. This FastAPI server also enables us to perform logging of the agent's execution trace, kill the agent if needed, etc.

Since we use 1 VM for each CUA, in order to run multiple CUAs in parallel, multiple VMs are needed (with different port settings). Please refer to TODO for more information.

# Setup

[TODO, insert commands]

Additionally, please take note that the following manual setup steps are recommended, as we were unfortunately unable to automate their setup:
- Firefox: For each VM, please navigate to localhost:608X (VNC endpoint), open the Firefox browser in the VM, go to about:config, and change the following parameters. These parameters are important, as they prevent the browser from recommending the agent to navigate to other subpages of our testing website. We observed that in some rare scenarios, the agent may click on past webpages visited (i.e. previous testcase urls), which will lead to inaccurate testcase execution trace logs.

[TODO]

# Running Testcases

[TODO]
