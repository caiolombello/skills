# Notation selection

Choose a notation because of the question it answers. Do not combine notations
merely to fit more information on one canvas.

## Decision matrix

| Question | Use | Core semantics |
|---|---|---|
| Who uses the system and what is outside it? | C4 System Context | People, software systems, external dependencies, relationships |
| What deployable units and stores make up the system? | C4 Container | Applications, services, data stores, technology, responsibility |
| Where does software run and fail? | C4 Deployment or topology | Environment, nodes, instances, zones, networks, placement |
| In what order do participants interact? | UML sequence | Lifelines, messages, activation, alternatives, loops |
| How does work cross roles or organizations? | BPMN collaboration | Pools, lanes, events, activities, gateways, message flows |
| How does information cross trust boundaries? | Data-flow/security view | Processes, stores, external entities, directed data flows, boundaries |
| How are network paths and controls connected? | Network topology | Zones, subnets, devices/services, routes, protocols, direction |
| What happened over time? | Timeline/incident narrative | Ordered evidence, state changes, decisions, causal links |
| What concept should a workshop understand? | Excalidraw narrative | Spatial story, contrast, progression, annotations |

## C4 rules

- Start with Context or Container. Add Component only for a specific design or
  ownership decision.
- Give every element a type, name, responsibility, and technology where useful.
- Label relationships with intent, not only protocol.
- Use separate views for current and target state unless comparison is the
  explicit question.
- Link related Context, Container, Component, Dynamic, and Deployment views
  rather than forcing them into one page.

Primary source: [C4 model diagrams](https://c4model.com/diagrams).

## UML sequence rules

- Put time top-to-bottom and participants left-to-right.
- Use solid request and dashed return only if that convention is declared.
- Use activation bars when active processing duration matters.
- Use `alt`, `opt`, `loop`, and `par` frames for control semantics; do
  not encode them as unlabeled crossing arrows.
- Keep infrastructure placement out of a sequence view.

Normative source: [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1).

## BPMN rules

- Use BPMN only when event, responsibility, gateway, and message-flow semantics
  matter.
- Put independent participants in pools and responsibilities in lanes.
- Use sequence flow inside a pool and message flow between pools.
- Distinguish start, intermediate, boundary, and end events.
- Do not use a generic diamond where the gateway type changes behavior.

Primary source: [OMG BPMN](https://www.omg.org/bpmn/).

## Deployment and topology rules

- Model environment before provider, account/project/subscription, region,
  network, zone/subnet, cluster, namespace, and workload.
- Place managed services where they operate, not where a private endpoint
  attaches.
- Show replicas, failure domains, ingress/egress, and failover only when
  verified.
- Separate logical dependency from physical network path when both matter.

## Progressive disclosure

Split the model when one view has multiple audiences, multiple primary reading
directions, or labels that become unreadable at the final delivery size.

Use this sequence when appropriate:

1. Executive/context view.
2. Engineering/container or service view.
3. Deployment/network view.
4. One or more runtime sequence/data-flow views.
5. Operational or security detail.

Each page must have its own title, question, scope, and legend. A multipage file
is not permission to hide an undocumented mega-diagram on page one.
