#Complete these codelabs:
Get started with Antigravity CLI
Explore Google Developer Knowledge MCP server in Google Antigravity

#1. Hands-on with Antigravity CLI

Before you do the setup and run Antigravity CLI, let us create a folder that we will be using as our home folder for all the projects that we create inside of it. This is a starting point for the Antigravity CLI to work with, though it will also reference some other folders on your system and which you will come to later, as needed.

Go ahead and create a sample folder (agy-cli-projects) and navigate to that via the commands shown below. If you prefer to use some other folder name, please do so.



Go ahead and create a sample folder (agy-cli-projects) and navigate to that via the commands shown below. If you prefer to use some other folder name, please do so.


mkdir agy-cli-projects
Let's navigate to that folder:


cd agy-cli-projects
The installation is straightforward and binaries are available across major Operating Systems. I have taken the commands to run in the terminal directly from the installation document:

macOS | Linux


curl -fsSL https://antigravity.google/cli/install.sh | bash
Windows PowerShell


irm https://antigravity.google/cli/install.ps1 | iex
Windows CMD


curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd
This should ideally setup and install the Antigravity CLI (agy) in your system and in the Path.



<img width="1422" height="659" alt="Screenshot 2026-06-20 at 2 41 28 PM" src="https://github.com/user-attachments/assets/c3ef743b-9fe3-4a7c-a56a-14a48361f713" />


Open Antigravity IDE, go to that folder: type command agy to launch antigravity cli

<img width="1158" height="449" alt="Screenshot 2026-06-20 at 2 56 33 PM" src="https://github.com/user-attachments/assets/75a38d9a-933d-47e8-a1f8-36d15f063bd4" />


Configuration / Settings
Go ahead and invoke the /config command. This will bring up various areas of Antigravity that you can customize based on your preferences. This includes the Color Scheme, Tool permission, telemetry settings and more.


The configuration settings need to be stored somewhere right? All of them get stored in ~/.gemini/antigravity-cli/settings.json

Tool Permission
An important setting to understand is the Tool Permission. This controls whether terminal commands require your approval before running. You can get to this via the /config command.


 Tool Permission
  > request-review (current)
    proceed-in-sandbox
    always-proceed
    strict
By default, it is set to request-review. Let's understand this in more detail. In Antigravity, Tool Permission settings control the balance between security (guarding your host system against unintended changes) and velocity (how autonomously the agent can work without pausing for your input).
> 
There are a few command line parameters that one can provide when you start Antigravity CLI. To get a full list of options, you can use the --help as shown below.


agy --help


Choose a specific model
The first one is to ask Antigravity CLI to use a specific Gemini mode. You can use the --model parameter to tell Antigravity CLI to use a specific model during its session only. This is very useful for the non-interactive mode that we mentioned in the previous section, where you would like to launch several agy sessions and use specific models for specific tasks.

But first, you need to know which models are available for Antigravity CLI. You can do that via the models subcommand as shown below:


agy models
This will list the models that are available for Antigravity CLI. A sample list is shown below:

Gemini 3.5 Flash (Medium)
Gemini 3.5 Flash (High)
Gemini 3.5 Flash (Low)
Gemini 3.1 Pro (Low)
Gemini 3.1 Pro (High)
Claude Sonnet 4.6 (Thinking)
Claude Opus 4.6 (Thinking)
GPT-OSS 120B (Medium)
You can use any of these model names to specify the model to be used for the session. You can do that via the --model command shown below:


agy --model "Gemini 3.5 Flash (Low)"
Once Antigravity CLI launches, you can check either via the /model command about the specific model that you asked it to use or look at the bottom right that shows the model used for the session


Living dangerously
If you like to live dangerously, then you can look for a very aptly named parameter called --dangerously-skip-permissions. This will auto approve all tool permissions. There will be no prompt asking you for permissions. So use it with care.

Launch Antigravity CLI via the following command:


agy --dangerously-skip-permissions
Then give the following prompt. Check that it did not ask me for any write file permissions.

6. Antigravity CLI - Shell mode
This is a good time to learn how to directly work with the Shell from within Antigravity CLI. You can go into shell mode by pressing ! in the message box. This will toggle to a Shell mode. You can get back by pressing ! again or by hitting the ESC key.

When in shell mode, you will see the ! at the start of the prompt as shown below:

8019057be515e68f.png

You can directly check using standard commands like pwd and ls. Please note that the commands assume a Linux type OS. If you are on another operating system (Windows), please use equivalent commands like (cd, dir and type).

#Use case to try out
ntigravity CLI can be applied to a wide range of use cases that apply to both developers and non-developers alike. Presented here are a few scenarios and depending on your area of interest, you can try any or all of them out.

In each of these cases, the prompt is provided. You are free to try this out in the Antigravity CLI interactive mode to understand better how Antigravity CLI goes about its task.

Vibe coding with Antigravity CLI
Let's use Antigravity CLI to vibe code an application. In this task, you will ask Antigravity CLI to generate an application and then push the initial version to a GitHub repository.

Prerequisite

To perform the tasks in this section, there are a few prerequisites:

Git
Antigravity CLI
Python 3 environment
Setup gh ( GitHub CLI tool).
Familiarity with Git basics and a bit of programming knowledge
We will assume that you have launched Antigravity CLI in a specific folder of your choice. In our case, we have launched Antigravity CLI from the initial home folder : agy-cli-projects and another folder bq-releases-notes inside of that.

Start with an initial prompt. Think of it as a specification for your application. Feel free to modify it as you see fit. Keep in mind that throughout the session with Antigravity CLI, it will ask you for permissions to create the files, etc. Do give the required permissions.

Please build a web application for me using Python Flask and plain vanilla HTML, JavaScript and CSS that fetches the BigQuery Release notes from (https://docs.cloud.google.com/feeds/bigquery-release-notes.xml) and shows them to me. 

A simple refresh button with a spinner is good enough, anytime I'd like to refresh the details. 

I would also like the ability to take any specific update, select it and then Tweet about it.


The next few prompts and responses are a sample flow that was observed. Antigravity CLI will come up with a plan and ask you for any confirmations / clarifications or go ahead. Please follow the instructions. As a sample, this is my sample conversational thread:


I will start by exploring the workspace to see if there is an existing structure or if this is a brand new project.                                                                   

● ListDir(/Users/romin/agy-cli-projects/bq-release-notes) (ctrl+o to expand)

 I will read the BigQuery release notes XML feed to understand its structure (Atom/RSS elements, entry/item elements, namespaces, dates, titles, content) so that we can parse it      
 correctly in the Python Flask backend.                                                                                                                                                

● ReadURL(https://docs.cloud.google.com/feeds/bigquery-release-notes.xml) (ctrl+o to expand)

 I will view the fetched feed content saved locally to understand its format and structure.                                                                                            

● Read(/Users/romin/.gemini/antigravity-cli/brain/116191af-e6ea-4ba5-aa23-62f995bd068a/.system_generated/steps/6/content.md) (ctrl+o to expand)

▸ Thought for 2s, 2.3k tokens
 Analyzing XML Feed Structure
 I will write the implementation plan detailing the architecture, design aesthetic, components, and verification steps for the BigQuery Release Notes Web Application. This plan will be
 written to the artifacts directory.                                                                                                                                                   

● Create(/Users/romin/.gemini/antigravity-cli/brain/116191af-e6ea-4ba5-aa23-62f995bd068a/implementation_plan.md) (ctrl+o to expand)

 I have created the implementation_plan.md to outline the design and architecture of the BigQuery Release Notes Web Application.
                                                                                                                                                                                       
 Please review the plan, especially the approach for the Twitter Composer & Preview Card, and let me know if you approve or if there are any adjustments you'd like to make!           


The next few prompts and responses are a sample flow that was observed. Antigravity CLI will come up with a plan and ask you for any confirmations / clarifications or go ahead. Please follow the instructions. As a sample, this is my sample conversational thread:

I will start by exploring the workspace to see if there is an existing structure or if this is a brand new project.                                                                   

● ListDir(/Users/romin/agy-cli-projects/bq-release-notes) (ctrl+o to expand)

 I will read the BigQuery release notes XML feed to understand its structure (Atom/RSS elements, entry/item elements, namespaces, dates, titles, content) so that we can parse it      
 correctly in the Python Flask backend.                                                                                                                                                

● ReadURL(https://docs.cloud.google.com/feeds/bigquery-release-notes.xml) (ctrl+o to expand)

 I will view the fetched feed content saved locally to understand its format and structure.                                                                                            

● Read(/Users/romin/.gemini/antigravity-cli/brain/116191af-e6ea-4ba5-aa23-62f995bd068a/.system_generated/steps/6/content.md) (ctrl+o to expand)

▸ Thought for 2s, 2.3k tokens
 Analyzing XML Feed Structure
 I will write the implementation plan detailing the architecture, design aesthetic, components, and verification steps for the BigQuery Release Notes Web Application. This plan will be
 written to the artifacts directory.                                                                                                                                                   

● Create(/Users/romin/.gemini/antigravity-cli/brain/116191af-e6ea-4ba5-aa23-62f995bd068a/implementation_plan.md) (ctrl+o to expand)

 I have created the implementation_plan.md to outline the design and architecture of the BigQuery Release Notes Web Application.
                                                                                                                                                                                       
 Please review the plan, especially the approach for the Twitter Composer & Preview Card, and let me know if you approve or if there are any adjustments you'd like to make!           

                                                                                                                                                           1 artifact · /artifact to review
                                                                                                                                                           1 artifact · /artifact to review
It's time to understand what Artifacts are in Antigravity. Artifacts are how the Antigravity CLI keeps us in the loop with an implementation plan, list of tasks that it is working on, verifiable outputs and more. These files are generated and are a record of the work that Antigravity is doing, its plan, task list and more.

Once it does that, it says " I have created the implementation_plan.md to outline the design and architecture of the BigQuery Release Notes Web Application. Please review the plan, especially the approach for the Twitter Composer & Preview Card, and let me know if you approve or if there are any adjustments you'd like to make!"

You can see that it also mentions in the bottom right, that there is 1 Artifact to review and in this case, it is the implementation_plan.md.

Give the command /artifact. This will display the artifact that it generated implementation_plan.md and you can use the arrow keys to open, approve, reject and so on. Just Escape and come back to the prompt, here you can approve it , if you'd like.

In our case, we are going to go with what it has generated and will be approving it. This kicks off the next set of steps, where it will start the implementation i.e. creating files, running a few commands, etc. You will be prompted to approve and give permission to execute, as required.

In our case, we gave it the approval to create the Python virtual environment, install the dependencies via requirements.txt and so on.

In the background, it has also created a task.md file as part of the tasks that it has to do based on the implementation plan and it ticks off the individual tasks, as it completes them. Once it is complete, it will let you know and you can check the application in the browser. Here is what it generated for us:


