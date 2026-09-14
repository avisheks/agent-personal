---
title: "Transforming HR Operations with LLM Agents in Action - deepsense.ai"
source: "https://deepsense.ai/case-studies/transforming-hr-operations-with-llm-agents-in-action/"
ingestedAt: "2026-07-30T16:15:08Z"
---
This project validated LLM-driven automation as a viable alternative to RPA in enterprise systems. By enabling natural language control over complex HR workflows, the agentic solution demonstrated its ability to save time, reduce training costs, and increase accessibility.

## In a Nutshell

### Client’s Challenge

As a global industrial leader operating in over 170 countries, the client faced a common challenge at scale: repetitive tasks within Workday, a widely used enterprise HR platform, were slowing down operations. Activities like uploading files, filling out forms, or updating user profiles required employees to manually navigate through multiple screens—an inefficient and error-prone process. The client aimed to streamline these workflows using natural language automation, leveraging AI techniques to overcome challenges where traditional RPA tools were limited due to system constraints.

### Our Solution

We developed an intelligent agent application powered by OpenAI’s large language models and a [browser-use](https://browser-use.com/) automation framework. The agent was capable of understanding natural language prompts, navigating Workday through browser-based actions, executing multi-step workflows, and logging each step for reusability and traceability.

While the initial documentation required refinement to suit agent-based execution, we adapted quickly by designing clear, step-by-step instructions for the agent. Despite operating in a restricted, limited-access environment, we successfully delivered a fully functional solution.

### Client’s Benefits

The AI Agent was successfully evaluated on a cross-sectional set of real-world Workday scenarios. We delivered production-ready, extensible code supported by clear documentation, making it easy to maintain and expand. The project demonstrated the feasibility of using LLM agents for process automation and made it simple to add new workflows going forward. Beyond saving time and improving user experience, the solution helped build internal support for broader automation initiatives.

## A Deep Dive

### **Overview**

This project marked a bold move toward intelligent automation at the enterprise level. In close collaboration with the client’s innovation and AI teams, we built a working prototype of an LLM-powered agent capable of navigating Workday, an internal workforce management system, using natural language commands.

The goal: automate complex, multi-step HR workflows with minimal manual effort.

Success was defined by:

  * Fully automated five real-world Workday use cases from end to end
  * Built a flexible solution that can be easily extended to other enterprise workflows
  * Delivered a robust, well-documented codebase ready for scale



This initiative demonstrated that LLM agents can significantly reduce repetitive workload in secure enterprise environments, laying the groundwork for broader, scalable automation across the organization.

### **Client**

The client is a global industrial powerhouse with over 130,000 employees and operations in more than 170 countries. Renowned for its legacy in manufacturing and mobility innovation, the organization also leads in digital transformation, extending its impact beyond production into engineering, lifestyle services, and customer experience.

With a strong track record in HR digitalization and process optimization, the client has consistently embraced new technologies to streamline operations. An early adopter of AI, they have previously explored RPA and scripted automation to reduce manual effort. However, recognizing the limitations of traditional approaches, they turned to large language model (LLM) agentic systems as a more scalable, flexible, and intuitive solution to drive the next wave of intelligent automation.

### **Challenge**

**Business Challenge**

The organization faced a growing volume of repetitive HR tasks spread across multiple departments, which placed a heavy burden on internal support teams. Routine operations within their enterprise HR platform required constant manual input, creating inefficiencies. Additionally, there was a strong need for a more intuitive interface that employees could use with little to no training.

**Technology Challenge**

There was no existing integration between the enterprise HR platform and large language models (LLMs), making it difficult to introduce AI-driven automation. The team had not yet established the necessary tooling to transform internal documentation into structured guidance that agents could follow. In addition, there was no existing control framework in place to reliably support deterministic, multi-step agent workflows. Previous attempts using traditional RPA solutions proved too fragile and complex to maintain over time.

### **Solution**

**Our Approach**

We approached the problem with an “agent-first” philosophy — giving the model a natural language instruction of what actions it needs to perform (e.g., entering a particular phrase in a search bar or pressing certain buttons) based on which it figures out the specific programmatic actions needed to take. We extended this idea to saving performed actions to a Python script that can be repeated in a deterministic manner later on. 

The following diagram illustrates the workflow for adding an automation for a new scenario:

  * Agent capable of automating Workday workflows via natural language.
  * Methodology for transforming actions performed by an agent into parametrizable, deterministic Python scripts.
  * The PDF2Prompt component to convert documentation into task prompts.
  * Evaluation framework to score agent performance across scenarios.
  * Codebase with modular architecture for future extensions.



**Technologies Used**

  * **LLMs:** Azure OpenAI (gpt-4o and gpt-4o-mini models)
  * **Frameworks and tools:** [browser-use](https://browser-use.com/) (emerging leader in the field, gaining over 60k GitHub stars in just 7 months), [neptune.ai](http://neptune.ai), jinja, HTML map support, logging and evaluation layer
  * **Cloud/Infra:** Ready for Azure deployment; support for Azure OpenAI API endpoints



### **Process**

**Requirements Gathering**

  * Identified high-volume, repeatable Workday tasks.
  * Mapped existing user pain points with internal stakeholders.



**Design & Planning**

  * Proposed agentic architecture.
  * Prioritized deterministic behavior for enterprise acceptance.



**Development**

  * Delivered and tested the local prototype with five diverse workflows.
  * Prepared methods for the smooth conversion of actions planned and performed by the agent to repeatable Python scripts.
  * Created a method to convert the PDF documentation of procedures to prompts understandable for web agents.



**MLOps & Integration**

  * Created modular layers for prompt validation and logging.
  * Ensured scalable deployment potential for broader rollout.



**Knowledge Transfer**

  * Ran workshops with client teams.
  * Delivered recorded walk-throughs and technical documentation.



### **Outcome**

**Quantitative Results**

  * 5 Workday scenarios fully automated via natural language with accuracy from 80% to 100% with agentic workflows.
  * 3x faster process design than with traditional RPA.
  * Cut implementation time for new scenarios from days to hours.



**Qualitative Results**

  * Validated the viability of LLM-based Workday automation.
  * Created conversion methods from LLM-based to a deterministic solution that reduces the costs to the infrastructure-related only.
  * Provided reusable, well-documented code for future pilots.
  * Created a foundation for advanced deterministic scripting.



**Lessons Learned**

  * Agents require highly detailed natural language prompts to achieve their goals, which makes humans indispensable in the workflow.
  * Combining HTML maps with screenshots of the webpage boosts the accuracy of the agents.
  * While PDF2Prompt can significantly speed up onboarding new workflows, the documentation of the procedures needs to stay up-to-date and be quite detailed.
  * Using web agents for the creation of repeatable deterministic scripts may be a sweet spot between the reduction of LLM costs, the reliability of the solution, and the amount of human labor.



### **Summary**

This project validated LLM-driven automation as a viable alternative to RPA in enterprise systems. By enabling natural language control over complex HR workflows, the agentic solution demonstrated its ability to save time, reduce training costs, and increase accessibility.

The groundwork is now in place for scaling this pilot into production, with a roadmap that includes adding automation for dozens of new scenarios, beta testing, full UI deployment, and utilizing desktop automation frameworks such as OpenAI’s Computer-Use API.

The next phase could change how enterprise users interact with software, moving from traditional, carefully crafted automation to AI-powered and more effective processes.