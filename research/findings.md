# Detailed findings

Research date: 2026-09-07. **Documented** describes a specification or official
project source. **Observed** describes inspected implementation code or existing
records, with its limits. **Recommendation** is a proposal for this project.
No external engine or conformance suite was executed. Exact versions, repository
revisions and inaccessible material are listed in [sources.md](sources.md).

## 1. The useful boundary crosses several standards

**Finding.** Process control, engineering meaning, tool communication, exchange
packaging and evidence are separate responsibilities. The strongest candidates
cover different parts of that chain. No reviewed evidence demonstrates that
one of them already preserves and independently executes the complete Wright
CAD case. That is a bounded research conclusion, not a claim about every product.

| Responsibility | Existing material to use | What remains to specify for this project |
|---|---|---|
| Executable steps and data/control flow | Open Workflow Specification (OWS), CWL, BPMN | One bounded supported profile; precise mappings and unsupported-feature behavior |
| Engineering artifacts and meaning | STEP, QIF, SysML/KerML, ISA-95/B2MML, AutomationML, UCUM | Which artifact/quantity contracts each step requires; acceptance evidence |
| Calls, resources and agent delegation | MCP, OPC UA, A2A | Binding from a process step to the author's intended provider and resource |
| Files, metadata and provenance | RO-Crate, PROV; optional OCI distribution | Authoritative entrypoint, complete dependency references, preservation and revision rules |
| Availability and recovery | Protocol errors plus receiving application | Common observable diagnostics/results; application-owned checks and user interaction |

**Recommendation.** Profile existing representations and define only their
missing connections. A JSON or YAML wrapper that invents its own entire task
graph would still be a new language; using familiar syntax would not avoid that.
The first exchange must ultimately demonstrate execution by an independent tool,
as well as preservation by a reader. Opaque archival alone meets only the latter.

## 2. Process candidates: go deepest on execution and binding

### Open Workflow Specification 1.0.3

**Documented.** The former Serverless Workflow repository now resolves to Open
Workflow Specification. Its tagged 1.0.3 reference defines JSON/YAML task
orchestration, data handling, branching, loops, parallel work, calls and errors.
The document's DSL version is distinct from the workflow's own namespace, name
and semantic version. MCP is an explicit call type with a method, parameters,
transport, client and timeout. This is directly relevant to fixed engineering
tool invocations. [Tagged reference](https://github.com/open-workflow-specification/specification/blob/v1.0.3/dsl-reference.md).

**Observed source inconsistencies.** The MCP reference labels `protocolVersion`
required while describing a default of `2025-06-18`. The tagged schema requires
only `method` and `transport` inside MCP arguments, and the example omits the
protocol version. The reference also requires initialization, so supplying a
2026 protocol string does not by itself implement the newer MCP lifecycle.
The example uses an unpinned package selector and inline token-like configuration;
it should not be copied as an engineering exchange fixture. These are source
observations, not results from executing the example.
[Schema](https://github.com/open-workflow-specification/specification/blob/v1.0.3/schema/workflow.yaml),
[example](https://github.com/open-workflow-specification/specification/blob/v1.0.3/examples/call-mcp.yaml).

**Implementation evidence.** The Java SDK includes a reference runtime but its
compatibility table associates SDK 7.x with specification 1.0.0. Synapse is a
separate runtime candidate. The inspected 1.0.3 CTK `call.feature` contains
HTTP/OpenAPI scenarios, without an MCP scenario in that file. Neither source
establishes an independently passing pair for the exact proposed MCP profile.
[Java SDK](https://github.com/open-workflow-specification/sdk-java/blob/c481ddb4d42dc068343542ebeaa158d399b694b4/README.md),
[Synapse](https://github.com/serverlessworkflow/synapse/tree/ba3fbfd5125995bba9fb5900aed181a0775d538c),
[call tests](https://github.com/open-workflow-specification/specification/blob/v1.0.3/ctk/features/call.feature).

**Recommendation.** OWS is the leading experiment for fixed MCP steps, conditional
on independent execution. Pin the protocol explicitly; use a narrow
`2025-11-25` experiment to match inspected Wright source, and assess
`2026-07-28` separately. Resolve the document/schema discrepancy in the profile
and propose an upstream clarification later. Use documented extension points
for provider requirements; prove that two engines enforce them. Do not put a
mandatory requirement in metadata that a normal executor can silently ignore
and then call that executor conformant to our profile.

### CWL 1.2.1

**Documented.** CWL models typed batch data flow. Its `requirements` are mandatory
for processing unless the user explicitly overrides them; `hints` may be
ignored. A named Solid Edge dependency therefore cannot be represented only as
a hint. Packed definitions use `$graph`; imports/includes compose documents,
but do not automatically collect datasets, installed software or CAD licenses.
`Operation` describes an abstract operation, not an implementation of an MCP
call. [Workflow specification](https://www.commonwl.org/v1.2/Workflow.html).

Command-line tools provide a practical boundary for deterministic calculations,
with declared inputs/outputs and software/container/resource requirements.
Those requirements do not create a CAD application's stateful document model.
[CommandLineTool specification](https://www.commonwl.org/v1.2/CommandLineTool.html).

**Implementation evidence.** cwltool is a reference implementation; CWL publishes
other implementations and versioned conformance cases. The 1.2.1 document/test
revision retains `cwlVersion: v1.2`. A test report needs both versions. Two
products sharing cwltool may supply useful integration evidence without proving
independent interpretation of the same semantics.
[cwltool revision](https://github.com/common-workflow-language/cwltool/tree/490c76c56ccccdd4194040dc0cf001fafb22d099),
[test/specification revision](https://github.com/common-workflow-language/cwl-v1.2/tree/551d58d409ef2a0fa2e3ab93b85167dd7d4b1833),
[implementation list](https://www.commonwl.org/implementations/).

**Recommendation.** Use CWL as the calculation baseline and a serious alternative
if the first milestone can remain batch-oriented. A CWL wrapper can invoke a
named MCP adapter, but that adapter and its binding contract become dependencies.
Do not describe this as native CWL CAD interoperability. Compare adapter effort,
failure visibility and independent support with OWS before selecting a baseline.

### BPMN 2.0.2 and DMN 1.5

**Documented.** BPMN covers executable process behavior and human/service tasks,
events and recovery constructs, while also defining model interchange and
diagram information. Modeling and execution conformance are distinct.
DMN supplies decision models, tables and FEEL; a decision output is not a
measurement, a person's approval or evidence that a provider executed anything.
[BPMN clauses 2, 7.7, 10, 13](https://www.omg.org/spec/BPMN/2.0.2/PDF),
[DMN 1.5](https://www.omg.org/spec/DMN/1.5).

**Implementation evidence.** Camunda service tasks use `zeebe:taskDefinition`
and job workers; Flowable supports its own implementation extensions. Standard
task shapes therefore do not imply a common executable CAD binding.
bpmn-moddle reads/writes models; the MIWG suite exercises model/diagram exchange.
Neither alone establishes independent runtime behavior. DMN's TCK adds
case-specific engine comparisons, a useful adoption practice.
[Camunda](https://docs.camunda.io/docs/components/modeler/bpmn/service-tasks/),
[Flowable](https://www.flowable.com/open-source/docs/bpmn/ch07b-BPMN-Constructs/),
[MIWG](https://github.com/bpmn-miwg/bpmn-miwg-test-suite/tree/121a0a5d6798233ee3ca09fba778e1ecc185ea14),
[DMN TCK](https://github.com/dmn-tck/tck/tree/20274cd2ba9cad805db6114f331c743f4b2603a1).

**Recommendation.** Keep BPMN as the human-approval comparison. Select it first
only if executable human workflow is a first-release requirement. Specify the
portable service/approval binding and test it across engines; preserving XML
alone is insufficient. Introduce DMN only when actual acceptance rules justify
a decision engine; simple numeric checks need not require one.

## 3. MCP explicitly: a protocol, with several identities and versions

**Documented.** MCP tool names are scoped to a server. Input/output schemas
describe structured data; annotations are not trusted authority. A JSON-RPC
error and a tool result with `isError` are different failure channels. A successful
tool result is not an engineering acceptance decision.
[MCP tools, 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

The current revision changes the lifecycle substantially: initialization and
protocol-level HTTP sessions are removed, request metadata carries version and
capability information, and discovery is explicit. Tasks move to an optional
extension. Older initialization-based clients cannot be assumed compatible.
[2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog),
[discovery](https://modelcontextprotocol.io/specification/2026-07-28/server/discover).
Wright's inspected gateway declares `2025-11-25`, whose lifecycle uses
initialization and negotiated capabilities.
[Prior lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
[Wright evidence](wright.md#contracts-versus-executable-paths).

**Registry evidence.** Official registry publishing checks namespace and package
ownership; `server.json` describes server versions, packages, remotes and runtime
configuration. It helps discover an intended implementation. It is not an
engineering process registry or proof that the right CAD application/document is
behind an endpoint. Publication also drops `_meta` keys outside the documented
publisher-provided namespace. Authoritative process data must not depend on
arbitrary registry metadata surviving publication.
[Pinned format](https://github.com/modelcontextprotocol/registry/blob/739b70e8bc1bea203c5a35ab699f1df51d091568/docs/reference/server-json/generic-server-json.md),
[publishing rules](https://github.com/modelcontextprotocol/registry/blob/739b70e8bc1bea203c5a35ab699f1df51d091568/docs/reference/server-json/official-registry-requirements.md).

**Implementation evidence.** Official TypeScript/Python SDKs, Inspector and a
conformance framework exist. The inspected conformance README still describes
initialization scenarios; an SDK release or Inspector session is not blanket
evidence for all 2026 protocol features. Version the exact client/server/test
combination. [Conformance revision](https://github.com/modelcontextprotocol/conformance/blob/a983ba93c91e0bb31d0b6849eeb52f0ad1083107/README.md),
[SDK revisions](sources.md#reproducible-repository-observations).

**Recommended identity separation.** This is proposed profile content, not a
claim that MCP already defines these fields:

| Identity | Preserve in the portable definition | Resolve or observe locally |
|---|---|---|
| Process | Stable identifier, definition revision, authoritative file digest | Local workspace/storage revision |
| MCP implementation | Publisher-controlled identity, package/repository identity, required release/revision | Installed package and observed implementation/version evidence |
| Application provider | The intended application inside a multi-provider server, e.g. Solid Edge | Provider selected by the server; reject a changed default when it differs |
| Operation | Server-scoped tool name, protocol, contract/schema version or scoped digest, argument/result mapping | Discovered tool and supported protocol/capabilities |
| Resource | Original artifact digest or provider-scoped object/revision, required representation | Path, document handle, account/tenant, permission and reachable resource |
| Connection | Logical binding reference and non-secret requirements | Endpoint/command, local server UUID, credentials, allowed paths |

A display name, a schema hash, or a reachable endpoint alone cannot establish
all these identities. A registry entry can anchor publisher/implementation
identity where one exists; do not invent an official registration for Wright's
observed Solid Edge server. Exact identity and compatibility evidence must be
captured in the first fixture. Self-reported names/versions also need a stated
trust basis, such as the known installed package or authenticated intended
service. Matching strings alone is not proof of the actual application behind
the server; the first experiment must declare what evidence it trusts.

## 4. Engineering and manufacturing standards supply meaning and artifacts

**SysML/KerML and Systems Modeling API — documented.** The final documents
provide engineering types, actions, requirements, quantities and verification
concepts. API projects, branches, commits and elements support model identity
and history; conformance scenarios cover API behavior. Public schemas, libraries
and pilot implementations are concrete assets, including a substantial
Java/Eclipse modeling stack. Model access does not execute Solid Edge operations.
[SysML Language, formal/2026-03-02](https://www.omg.org/spec/SysML/2.0/Language/PDF),
[API, formal/2026-03-04](https://www.omg.org/spec/SystemsModelingAPI/1.0/PDF),
[pilot revision](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/tree/287bd59befe4971eb24bc33c1c46361a0ea14005).
**Recommendation:** reference these concepts and link versioned engineering
models; avoid requiring a full modeling-language implementation for a small
tool process. Do not invent parallel requirements/model repositories initially.

**STEP AP242/AP238 — documented scope, limited normative access.** AP242 covers
managed model-based engineering product exchange; AP238 addresses manufacturing
using machining information. The ISO catalog editions reviewed are 2025 ed. 4
and 2022 ed. 3 respectively. Full normative texts were not obtained.
[AP242](https://www.iso.org/standard/84300.html),
[AP238](https://www.iso.org/standard/84898.html).
STEPcode provides EXPRESS/data-access implementation work; NIST's analyzer
checks file information, PMI and validation properties. Those are valuable
checks, not proof of every geometry or application-protocol requirement.
CAx implementor groups publish versioned practices and cross-vendor test work.
[STEPcode](https://github.com/stepcode/stepcode),
[NIST analyzer](https://www.nist.gov/services-resources/software/step-file-analyzer-and-viewer),
[CAx practices](https://www.mbx-if.org/home/cax/recpractices/).
**Recommendation:** declare the required native and neutral representations and
their verification criteria independently. A STEP artifact cannot silently
replace the named provider, sheet-metal features or an editable native document.
Reuse the CAx pattern of shared samples plus measured expected properties.

**ISA-95/B2MML — documented.** This family addresses enterprise/manufacturing
operations and resource information. Its parts have different revision years.
MESA's B2MML 7 supplies XML schemas/examples corresponding to specified ISA-95
updates; the repository explicitly labels its generated JSON schema untested.
An XSD is not an execution engine. Full ISA texts were not accessed.
[ISA index](https://www.isa.org/standards-and-publications/isa-standards/find-isa-standards-by-topic),
[MESA revision](https://github.com/MESAInternational/B2MML-BatchML/tree/65cc66534343c86a1ce953561e121f906a0a0cbe).
**Recommendation:** reuse versioned manufacturing payloads when operations,
equipment or personnel exchange is required; do not force every CAD block into
an enterprise manufacturing model.

**AutomationML — documented.** IEC 62714-1:2018 and associated material cover
automation-engineering interchange using CAEX. Association guidance includes
libraries and a multi-file container; Aml.Engine supplies .NET APIs for CAEX
3.0/2.15. Container guidance does not define every tool's exchange procedure.
Full IEC text was not obtained.
[IEC catalog](https://webstore.iec.ch/en/publication/32339),
[association material](https://www.automationml.org/about-automationml/specifications/),
[Aml.Engine revision](https://github.com/AutomationML/AMLEngine2.1/tree/098106acd50ca74c10a12d2cbecdae047c1f9b4b).
**Recommendation:** reference topology, library and external-file relationships
for plant/toolchain cases. Library availability and process execution still need
separate receiving-application checks.

**QIF — documented.** QIF 3/ISO 23952:2020 links product characteristics with
quality information. Community code contains C++/C#/Python bindings and samples;
validation tools combine XSD and additional XSLT checks. Full ISO text and
member-only development material were not obtained.
[ISO catalog](https://www.iso.org/standard/77461.html),
[community revision](https://github.com/QualityInformationFramework/qif-community/tree/64268c175a3058d09db29c14869b94b781518709),
[validator revision](https://github.com/QualityInformationFramework/qif-validation-tools/tree/39843e5cc696c21ce0f8b20537d01893198f3854).
**Recommendation:** prefer QIF artifacts for actual inspection exchange, with
part/plan/feature identity and measurement provenance. Schema validity does not
establish calibrated measurement, completeness or authorized approval.

**A2A — documented.** Agent cards describe provider, skills, interfaces,
capabilities and authentication requirements. Tasks, messages and artifacts
support delegation, including failed, rejected, input-required and
authentication-required outcomes. Official SDKs and a TCK exist; their exact
compatibility must be checked separately from protocol release 1.0.1.
[Specification](https://a2a-protocol.org/latest/specification/),
[release](https://github.com/a2aproject/A2A/releases/tag/v1.0.1),
[TCK](https://github.com/a2aproject/a2a-tck).
**Recommendation:** an A2A message could communicate an identified process
package and return result references. Define that optional convention if needed;
an agent skill description or completed task does not disclose the internal
recipe or prove it used the named CAD provider.

**OPC UA — documented.** The service model carries explicit status quality and
supports industrial resource communication. The Foundation publishes a .NET
stack, while its CTT access page restricts the compliance tool to corporate
members. Neither restricted test contents nor exact coverage were inspected.
[Services](https://reference.opcfoundation.org/Core/Part4/v105/docs/),
[stack revision](https://github.com/OPCFoundation/UA-.NETStandard/tree/1af191ec268a85c260a56d5bc65cd96d6bac42fa),
[CTT](https://opcfoundation.org/developer-tools/certification-test-tools/opc-ua-compliance-test-tool-uactt/).
**Recommendation:** reference it for equipment/service adapters and preserve
result quality. Connection success is separate from the correctness of a
manufacturing operation or a portable process definition.

**Other useful boundaries.** FMI/SSP supply simulation models/system packages;
embedded binaries can still be unavailable on an execution platform. AAS
supplies digital-twin resource/submodel exchange; SCXML supplies state-machine
execution. Official Reference FMUs, BaSyx and Commons SCXML provide concrete
implementation starting points, with version limits in
[S12](sources.md#s12-additional-boundaries). **Recommendation:** link or wrap these
at genuine domain boundaries, without adding them to every process's minimum
dependency set.

## 5. Packaging, sharing and dependency semantics

**Documented.** RO-Crate 1.2 uses JSON-LD metadata to describe a research object
and local or external data. Workflow Run RO-Crate profiles specialize execution
provenance. PROV supplies entity/activity/agent relationships. These describe
objects and claims; they do not install software, authorize access or establish
that an assertion is true. OCI manifests offer digest-based distribution as an
optional transport, without defining engineering process meaning.
[RO-Crate 1.2](https://www.researchobject.org/ro-crate/specification/1.2/),
[data entities](https://www.researchobject.org/ro-crate/specification/1.2/data-entities.html),
[Workflow Run RO-Crate](https://www.researchobject.org/workflow-run-crate/),
[PROV overview](https://www.w3.org/TR/prov-overview/),
[OCI manifest](https://specs.opencontainers.org/image-spec/manifest/).

Python dependency specifiers and platform tags demonstrate explicit version and
environment constraints. Those rules are Python-specific. A marker that omits
a package on another platform is the wrong analogy for deleting a required
Solid Edge block: that block stays required even when unavailable.
[Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/),
[platform tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/).

**Recommendation.** Trial a small RO-Crate profile containing one authoritative
workflow entrypoint, required profile versions, intended providers/resources,
input artifacts or external references, output contracts and acceptance checks.
Use a directory for inspection and a single-file archive for transfer; prove
that both carry the same payload identities. Exact archive rules remain to be
chosen. A Git repository, file attachment, object store or optional registry
may distribute the same package without becoming its semantic authority.

Retain original Wright source and layout as identified source artifacts when
exporting a supported subset. Clearly name which representation is executable
authority. Do not create two independently editable authoritative graphs. An
export that changes AI tasks into fixed calls is a new process unless equivalence
has been established; merely embedding the original source does not establish it.

Pin immutable artifact bytes and exact tested provider versions initially.
Keep package-profile, workflow-language, process, protocol, SDK, server,
application, tool-contract and resource versions separate. Declare a version
scheme before allowing ranges: date-based protocols and vendor builds are not
automatically SemVer. Raw file SHA-256 supports exact preservation; portable
semantic hashing requires additional canonicalization rules and should wait.

Local paths and session document handles are locators, not sufficient shared
identities. A native file can travel with a digest; a cloud object may require
provider, tenant/workspace, object ID and immutable revision. Unavailable external
content stays an explicit requirement. A same-provider connection mapping can
change without rewriting the process; selecting a different implementation or
application is an explicit process edit under the author's compatibility policy.

## 6. Validation, unavailable resources and failure

**Documented precedents.** JSON Schema validates structure, with an official test
suite. CWL separates required features from hints. MCP distinguishes protocol
and tool failures. OPC UA distinguishes Good, Uncertain and Bad result quality;
clients must inspect it. These are useful pieces, but not one complete lifecycle.
[JSON Schema 2020-12](https://json-schema.org/draft/2020-12),
[CWL](https://www.commonwl.org/v1.2/Workflow.html),
[MCP tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools),
[OPC UA StatusCode](https://reference.opcfoundation.org/Core/Part4/v105/docs/7.38).

**Recommended distinctions.** These are conceptual categories, not new normative
wire status names:

| Condition | Meaning and required observable outcome |
|---|---|
| Invalid definition | A known schema or semantic invariant fails; preserve received bytes and locate the defect |
| Unsupported definition feature | Required language/profile/extension semantics cannot be understood; preserve it, decline affected interpretation/execution, avoid claiming validity |
| Valid but unavailable | Understood definition; intended provider, platform, permission, resource or version is unavailable; retain all blocks and explain the affected dependency |
| Ready | Local binding currently satisfies declared prerequisites; later failure remains possible |
| Execution failed | Operation returned a tool/protocol/domain failure; retain original cause, task identity and trustworthy partial outputs |
| Outcome unknown | Connection lost after a possible mutation, or durable state is insufficient; do not infer rollback or repeat a mutation blindly |
| Acceptance failed / indeterminate / not run | Execution evidence is outside tolerance, inadequate, or missing; distinguish these from execution state |
| Approval pending / rejected / granted | A separate authorized human decision concerning exact result/definition revisions |

The application performs checks and presents diagnostics; the portable profile
defines the requirements and observations needed to test faithful behavior.
Import/open performs no engineering operation. A missing dependency gates the
affected work and its dependents; a first implementation can conservatively
block the whole run. If independent branches are allowed to proceed, that policy
and partial outcome must be explicit and tested.

Error information should include a stable category, process/block pointer,
intended dependency, observed mismatch, cause and recoverable next action.
Retain native protocol details without inventing a new MCP wire error system.
HTTP APIs can use RFC 9457; OWS's older RFC 7807 reference should be mapped
deliberately. [RFC 9457](https://datatracker.ietf.org/doc/html/rfc9457).

A run record should identify the exact definition, inputs, provider revisions,
calls, outputs and acceptance evidence. Partial artifacts need resource identity,
revision and durability. Successful API status, AI narrative and file existence
are insufficient engineering oracles. UCUM can encode units, but dimensional
meaning, uncertainty and tolerances still require declared checks.
[UCUM 2.2](https://ucum.org/ucum), [Wright observations](wright.md).

## 7. Adoption, documentation, governance and licensing

**Documented adoption assets.** CWL offers reference tooling and conformance
cases; OWS offers a tagged reference, schema, examples and CTK; MCP offers SDKs,
Inspector, registry and an enhancement-proposal process. MIWG and CAx test
exchanges, while DMN publishes case/engine results. These make implementation
problems concrete and comparable. They do not guarantee adoption, and example
quality and exact version coverage still need review.
[CWL tooling](https://github.com/common-workflow-language/cwltool),
[OWS CTK](https://github.com/open-workflow-specification/specification/tree/v1.0.3/ctk),
[MCP proposals](https://modelcontextprotocol.io/community/sep-guidelines),
[MIWG](https://github.com/bpmn-miwg/bpmn-miwg-test-suite),
[CAx](https://www.mbx-if.org/home/cax/implementor-group/),
[DMN results](https://dmn-tck.github.io/tck/).

**Recommended implementation practice.** Publish a short implementer path:
inspect a package without Wright, validate a good and a deliberately unavailable
example, bind the intended provider, run a small calculation, and inspect a
failure/acceptance report. Include exact commands only after they work against
pinned releases. Publish machine-readable fixtures, expected diagnostics and
per-case reports; identify shared code between purportedly independent engines.
Measure implementation effort during the experiment rather than inventing a
line-count or schedule estimate. Keep a small supported-feature list and an
extension namespace policy. A badge should name profile, suite version,
implementation revision and passing cases; an unqualified “compliant” badge
would hide the limitations that matter here.

| Route | Evidence and participation needed | Recommendation and tradeoff |
|---|---|---|
| Project-led proposed specification | Maintainers, public change rationale once publication is authorized, versioned tests | Start here; quick correction, but authority is concentrated |
| Multi-vendor working group | Independent implementers, shared cases, documented disagreements and decision rules | Next useful step; broader requirements, slower consensus |
| Foundation/consortium stewardship | Sustainable maintainers, participation and IP policies, actual transfer agreement | Consider when recurring coordination needs justify overhead; affiliation is not conformance |
| Formal standards-body route | Stable scope, interoperable implementations, stakeholder participation and required process/IP review | Later; durability and recognition trade against time, cost and possible access barriers |

This comparison is an assessment informed by the documented
[CWL governance](https://www.commonwl.org/governance/),
[MCP governance](https://modelcontextprotocol.io/community/governance),
[OMG process](https://www.omg.org/gettingstarted/processintro.htm) and
[ISO stages](https://www.iso.org/stages-and-resources-for-standards-development.html).
It makes no claim that these organizations would accept this work.

**Licensing options, not a selection.** An Apache-style license for both text
and code is one option; separate document and permissive code/schema licenses
are another. MCP's governance illustrates a split between specification/code
and other documentation, with exceptions. A future standards body may impose
its own contribution and patent policy. Copyright permissions, contributor
patent commitments, third-party dependencies and use of conformance marks are
separate decisions. Apache 2.0 includes a scoped contributor patent grant;
CC BY 4.0 does not grant patent rights. Neither supplies general legal clearance.
[MCP policy](https://modelcontextprotocol.io/community/governance),
[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode),
[W3C patent-policy example](https://www.w3.org/policies/patent-policy/).

**Recommendation.** Decide document/code/test-data rights and contributor terms
before inviting external contributions or distributing implementation assets.
Do not import paid standards or vendor sample models into this repository based
on an assumption of permission. No license, visibility change, external contact
or standards submission is made by this research.

The [worked cases](../use-cases/interoperability.md) turn these findings into
testable behavior. The [proposed decision](../decisions/001-first-boundary.md)
sets priorities and records unresolved choices.
