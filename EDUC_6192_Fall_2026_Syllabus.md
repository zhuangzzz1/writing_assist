# **Applied Assignment 4:** 

# **Agent-based Educational Application**

Weight: 15% of final course grade

Due: November 3, 2026

## **Purpose**

In this assignment, you will design, test, and improve an agent-based educational application using either a single-agent or multi-agent architecture. You may transform an earlier workflow or application, or customize a supported agent template or agent-building environment.

The purpose is to practice deciding when agent-controlled behavior is useful; defining agent roles, instructions, responsibilities, and boundaries; and designing appropriate behavior for clarification, action selection, coordination (when applicable), completion, stopping, and human review.

The goal is not to create a highly complex or fully autonomous system. Select the simplest architecture that adequately supports the educational task. Single-agent and multi-agent designs are architectural choices, not sequential assignment requirements. Direct API programming is not required unless you choose an API-based implementation.

## **Learning Outcomes**

After completing this assignment, you should be able to:

1. Distinguish a fixed workflow, a single-agent design, and a multi-agent design, and explain when agent-controlled decision making is useful for an educational task.  
2. Define an agent-based application’s educational purpose, intended users, agent roles or responsibilities, and important boundaries.  
3. Design agent instructions that support appropriate use of task context, action selection, and, when multiple agents are used, coordination, handoffs, or information sharing.  
4. Design appropriate clarification behavior when important information is missing or ambiguous.  
5. Define the appropriate conditions for completion, stopping, and human review.  
6. Review agent behavior across different situations and revise the agent-based application based on observed problems.  
7. Select and justify the simplest architecture that adequately supports the educational task, considering educational fit, reliability, complexity, cost, and maintainability.  
8. Identify limitations, risks, and situations requiring human oversight in educational use.

## **Assignment Scenario**

Select a realistic educational use case related to your academic program, research, teaching, professional experience, or planned course project.

You may continue using an educational use case, workflow, or application from an earlier assignment.

Examples include a tutoring assistant, study-support agent, formative-feedback agent, instructional assistant, learning-resource assistant, reflection coach, advising assistant, or another agent with a clear educational purpose.

The task should require at least one meaningful agent-controlled decision about how to proceed rather than simply follow the same fixed sequence for every request. You may use one agent or multiple agents. If you use multiple agents, each agent should have a distinct and necessary role; do not add agents simply to increase technical complexity.

## **Assignment Tasks**

### **Part 1\. Define the Educational Need and Agent Architecture**

Briefly describe:

1. Intended users, educational needs, and main task.  
2. Information or input that the user will provide.  
3. Your proposed architecture: single-agent or multi-agent.  
4. The responsibilities and important boundaries of the agent or agents.  
5. Actions, information, functions, tools, or other resources available to the agent or agents, when applicable.  
6. When the agent or system should ask the user for clarification.  
7. If you use multiple agents, the distinct roles and how tasks, handoffs, or information will be coordinated. If you use one agent, briefly explain why additional agents are unnecessary.  
8. When the task should be considered complete.  
9. When the agent or system should stop or request human assistance.  
10. What a successful performance would look like and why your chosen architecture is the simplest appropriate design for this educational task.

Keep this section concise and focused on essential design decisions.

### **Part 2\. Create Agent-Based Application Version 1**

Create or customize an agent-based educational application using one agent or multiple agents. You may transform an earlier workflow or application, or use a supported agent template or agent-building environment.

Your agent-based application should demonstrate, when relevant:

1. Clear instructions defining the application’s educational purpose and the role or roles of the agent or agents.  
2. Appropriate use of user-provided information and relevant task context.  
3. The ability to select an appropriate action or response.  
4. The ability to ask for clarification when essential information is missing or ambiguous.  
5. Appropriate completion, stopping, and human review behavior.  
6. If multiple agents are used, distinct and necessary roles with appropriate coordination, handoff, or information-sharing behavior.

Use one representative educational request to confirm that the main interaction works.

Save appropriate evidence of Agent-Based Application Version 1\. Evidence may include screenshots, selected agent instructions, configuration settings, selected code or notebook excerpts, or a brief record of the application’s or agents’ actions.

**Label this: Agent-Based Application Version 1**

### **Part 3\. Review Agent-Based Application Version 1**

Test Agent-Based Application Version 1 using three situations:

1. Normal case: Provide enough information for the agent-based application to complete its intended educational task.  
2. Incomplete or ambiguous case: Omit or make unclear an important piece of information, and examine whether the agent-based application asks for appropriate clarification.  
3. Boundary or human-review case: Provide a situation in which the agent-based application should recognize a limitation, stop, or request human assistance.

For each case, briefly document:

1. The input or task.  
2. The important action or decision made by the application or agent(s).  
3. The resulting output or interaction.  
4. When multiple agents are used, note any important coordination, handoff, duplicated work, conflicting output, or information-sharing issues observed in the case.

Consider whether the agent-based application remained within its educational purpose, selected appropriate actions, requested clarification when needed, recognized completion, and stopped or requested human assistance appropriately. When multiple agents are used, also consider whether the roles and coordination are necessary, clear, and efficient.

Identify the two or three most important problems to address in the revised version.

You do not need to create a formal evaluation set for this assignment.

### **Part 4\. Create and Verify Agent-Based Application Version 2**

Revise the agent-based application based on the problems identified in Part 3\.

Revisions may involve agent instructions, responsibilities, boundaries, behavior clarification, action-selection guidance, completion conditions, stopping conditions, human-review conditions, or, when multiple agents are used, role definitions, routing, handoffs, shared information, or coordination.

Before finalizing Agent-Based Application Version 2, submit the draft to JeepyTA for formative feedback. Provide sufficient information for review, such as a working link, required files, selected instructions or configuration, and a brief description of the educational purpose, intended users, and chosen architecture.

Review the feedback and use your own judgment to determine which suggestions are relevant. You are not required to accept every JeepyTA suggestion.

Label the revised application: Agent-Based Application Version 2

Repeat the same three situations used with Agent-Based Application Version 1\.

Provide before-and-after evidence and briefly explain what you changed, why you changed it, and whether Agent-Based Application Version 2 behaved more appropriately. If you changed the architecture or number of agents, explain why the revised architecture better fits the educational task.

If an important problem remains, identify it.

### **Part 5\. Explain Your Agent Architecture and  Development Process**

Briefly provide:

1. The major instructions or configuration used to define the agent-based application’s purpose and behavior, and whether you used a single-agent or multi-agent architecture.  
2. Two important revisions you made while developing the agent-based application.  
3. If you used multiple agents, how you define distinct roles and coordination or handoffs; if you used one agent, why additional agents were unnecessary.  
4. One LLM- or tool-generated suggestion that you accepted, modified, or rejected, and why.  
5. One example showing how your own judgment influenced the final architecture or agent behavior.

You do not need to submit the complete chat transcript, complete codebase, or every intermediate version.

### **Part 6\. Brief Reflection**

In approximately 200–300 words, explain:

1. What did you learn about when agent-based behavior is preferable to a fixed workflow and when one agent may be preferable to multiple agents?  
2. Why is your final architecture the simplest one that adequately supports the educational task, and what evidence from your testing supports that choice?  
3. What important limitations or risks remain, and under what conditions should a human review or take over the task?

## **What to Submit**

Submit one document containing:

1. Educational Need and Agent Architecture  
2. Agent-Based Application Version 1 and Evidence  
3. Review of Agent-Based Application Version 1  
4. Agent-Based Application Version 2, Before-and-After Evidence, and Verification  
5. Agent Architecture and Development Process  
6. Brief Reflection  
7. Agent-Based Application Access, including a working link or required application, notebook, configuration, or other files when applicable  
8. AI Use Acknowledgment identifying the generative AI tool used, its purpose, and how it contributed to your work

Do not include API keys, passwords, confidential educational data, or personally identifiable information.

## **Grading Criteria**

Rubric weights below are percentages of this assignment grade.

| Criteria | Full | Partial | Zero | Weight |
| ----- | ----- | ----- | ----- | :---: |
| **Educational Need and Agent Architecture** | The educational need, intended users, agent purpose, chosen architecture, responsibilities, boundaries, clarification behavior, completion conditions, and human-review conditions are clearly defined and aligned with the proposed application. The architecture choice is appropriately justified. | The overall design is appropriate, but one or more important elements or the architecture justification are unclear, incomplete, or weakly aligned. | Major design elements are missing or unclear, or the chosen architecture does not meaningfully address the educational need. | 20% |
| **Functional Agent-Based Application** | Agent-Based Application Version 2 functions as an educational application, supports the intended task, and demonstrates meaningful agent-controlled action or decision making. If multiple agents are used, their roles are distinct and necessary. | The application is partially functional or supports the task, but important problems remain with interaction, agent-controlled behavior, or the necessity or clarity of multiple-agent roles. | The application is not functional or does not demonstrate meaningful agent-based educational behavior. | 20% |
| **Agent Behavior, Coordination, and Boundaries** | The application appropriately handles the normal, incomplete, or ambiguous, and boundary or human-review cases, including clarification, completion, stopping, and human-review behavior. When multiple agents are used, coordination, handoffs, and information sharing are appropriate and efficient. | The application handles some situations appropriately, but important problems remain in clarification, completion, stopping, human review, or, when applicable, coordination or handoffs. | Appropriate agent behavior or boundaries are largely absent, or the application fails to clarify, stop, request human review, or coordinate appropriately when necessary. | 20% |
| **Iterative Testing and Improvement** | The student identifies meaningful problems in Version 1, makes purposeful revisions, retests the same three situations, and provides clear before-and-after evidence of improvement. Any architecture change is evidence-based and justified. | Testing and revision are present but limited, weakly justified, or only partially connected to evidence from Version 1; architecture changes, if any, are weakly justified. | Little or no meaningful testing, revision, retesting, or evidence of improvement is demonstrated. | 20% |
| **Architecture Justification, Development Evidence, and Reflection** | The student documents important development decisions, critically reviews AI-generated suggestions, justifies the final architecture as the simplest adequate design, and thoughtfully explains learning, remaining limitations, risks, and appropriate human oversight. | Development evidence and reflection are present, but the justification of the architecture, critical review, or consideration of limitations and human oversight is incomplete or superficial. | Development evidence or reflection is missing, or there is little evidence of architecture justification, critical review, or human judgment. | 20% |
| **Total** |   |   |   | 100% |

## **Where to Submit**

1. Submit drafts in PDF through JeepyTA using the following file name format:  
   FirstName\_LastName\_Assignment\_Number  
2. Submit the link to your JeepyTA assignment on Canvas.   
3. Submit or link the application, notebook, configuration, or other files required to review the functional agent-based educational application.

