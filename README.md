# Google 5-Day Agentic AI Learning & Capstone

A learning repository containing notes, exercises, experiments, and a capstone project developed while exploring agentic AI concepts.

The most substantial portfolio project in this repository is **DevLoop**, a multi-agent software development lifecycle (SDLC) automation prototype built around Google ADK, MCP tools, a Spring Boot service, and a React interface.

## Start here

| Area | Contents |
|---|---|
| **Capstone: DevLoop** | Multi-agent workflow, architecture, implementation, demo scenarios, setup, and security notes |
| Day 1–5 | Course exercises and daily learning material |
| Capstone documentation | Design notes, implementation logs, test evidence, and demo assets |

[Explore the DevLoop capstone](./CapstoneProject/README.md)

## Featured project: DevLoop

DevLoop explores how specialized agents can collaborate across a software delivery workflow:

1. Read and classify a work item.
2. Analyze a codebase and propose a change plan.
3. Implement backend or frontend changes.
4. Generate and run tests.
5. Verify application behavior through API checks.
6. Prepare a GitLab merge request.
7. Review changes, apply feedback, and run security checks.

The capstone includes Python agent orchestration, custom MCP servers, a Java 21 / Spring Boot backend, and a React frontend. See the [capstone README](./CapstoneProject/README.md) for the architecture, prerequisites, configuration, and run instructions.

## Repository map

```text
Google_5days_agentic_ai/
├── Day1/ ... Day5/       # Daily course exercises and learning material
├── CapstoneProject/
│   ├── agents/           # Specialized agent implementations
│   ├── mcp_servers/      # Tool servers and toolsets
│   ├── backend/          # Spring Boot / Java backend
│   ├── frontend/         # React frontend
│   ├── docs/             # Architecture, run logs, and test evidence
│   └── README.md         # Capstone guide
└── README.md
```

## Getting started

For the capstone, follow the dedicated [DevLoop setup guide](./CapstoneProject/README.md). It documents required Python, Java, Node.js, Google AI, and GitLab configuration.

**Security:** Never commit real API keys, GitLab tokens, `.env` files, or other credentials. Use the provided example environment file and rotate any credential that may have been exposed.

## Related engineering portfolio

- [Spring Boot projects](https://github.com/NeelimaBarji/SpringBoot-Projects)
- [Java, Spring Boot, system design, and AI preparation](https://github.com/NeelimaBarji/preparation_material)
- [Angular projects](https://github.com/NeelimaBarji/AngularRepo)

---

*Learning repository and applied agentic AI portfolio project.*