#Google Developer Knowledge MCP server in Google Antigravity.md


##Introduction

Google Developer Knowledge is the canonical, machine-readable source of Google's public developer documentation. 
It's programmatically accessible via Application Programming Interface (API) and Model Context Protocol (MCP) so that developers can integrate it into applications and workflows.


In this codelab, you will learn how to install and use the Developer Knowledge MCP from Antigravity 2.0, IDE, and/or CLI. MCP is an open standard that enables AI models to securely use tools provided by remote servers. 
You will set up Antigravity to interact with the knowledge base without writing any code!

#What you'll do
Enable the Developer Knowledge API in your Google Cloud project.
Configure Antigravity to access the Developer Knowledge MCP.
Test the integration with a few prompts.


#What you'll need
A web browser such as Chrome
A Google Cloud project (billing is not required).
Antigravity 2.0, IDE, and/or CLI installed on your local machine. You can find more detail and installation guidance from the official website.


Explore more MCPs and tools
In this codelab we only cover a few basic examples of what can be done using the Google Developer Knowledge MCP server. 
To see the full list of Google MCP servers and tools available, refer to the Supported Products.

## Configure Cloud Project:

Create or Select a Google Cloud project
In the Google Cloud Console, select or create a Google Cloud project.

Enable the API
To use the Developer Knowledge MCP server, you must enable the standard Developer Knowledge API.

Create the API key
To use the Developer Knowledge MCP server, you must use an API key. In the Google Cloud Console, do the following:

Go to APIs & Services > Credentials.
Go to Credentials

Click + Create credentials, then select API key from the menu.
Set Name with an arbitrary name such as Antigravity.
Click the Select API restrictions drop-down, type Developer Knowledge API, check the result, then click OK.

Click Create.
Your API key is now displayed on the confirmation screen. Copy it to your clipboard, you'll need it to configure Antigravity in the next steps.
Important: Never share an API key publicly. The one you see in the following screenshot is fake, it was added for illustration purposes only.




