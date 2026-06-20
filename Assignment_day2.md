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

