# Source register

Research and retrieval date: **2026-09-07**. Linked artifacts located without
full inspection are identified below. Dates distinguish publication,
release, and observed revision; an undated website is not assigned an invented
publication date. Specifications are authoritative for their stated versions;
project documentation describes implementations. None of the referenced
external test suites was executed for this report. Wright's separate evidence
and file identities are in [wright.md](wright.md).

Exact repository HEADs were obtained through public GitHub metadata reads.
Those snapshots are not necessarily released versions and are not claimed to
implement every feature in a newer specification. “Not archived” was verified
for every repository in the revision table. Remaining implementation links are
dated documentation observations, explicitly unpinned; they cannot support a
reproducible conformance claim. No copyrighted standards are mirrored here.

## S01 MCP

- [Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28),
  [changes from 2025-11-25](https://modelcontextprotocol.io/specification/2026-07-28/changelog),
  [tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools),
  [discovery](https://modelcontextprotocol.io/specification/2026-07-28/server/discover).
  Dated protocol revision; current specification landing page resolved here.
- [2025-11-25 lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)
  is the version identified in Wright source, not the latest revision.
- [Registry overview](https://modelcontextprotocol.io/registry/about),
  [pinned server.json format](https://github.com/modelcontextprotocol/registry/blob/739b70e8bc1bea203c5a35ab699f1df51d091568/docs/reference/server-json/generic-server-json.md),
  [schema](https://github.com/modelcontextprotocol/registry/blob/739b70e8bc1bea203c5a35ab699f1df51d091568/docs/reference/server-json/draft/server.schema.json),
  [official publishing requirements](https://github.com/modelcontextprotocol/registry/blob/739b70e8bc1bea203c5a35ab699f1df51d091568/docs/reference/server-json/official-registry-requirements.md).
  The draft schema is pinned by commit; do not treat its `main`-based `$id` as immutable.
  Registry service release observed: [v1.8.1](https://github.com/modelcontextprotocol/registry/releases/tag/v1.8.1), 2026-08-06.
- [Conformance README](https://github.com/modelcontextprotocol/conformance/blob/a983ba93c91e0bb31d0b6849eeb52f0ad1083107/README.md),
  [Inspector](https://github.com/modelcontextprotocol/inspector),
  [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk),
  [Python SDK v2.2.0](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.2.0),
  released 2026-09-07. SDK protocol coverage requires its own checks.
- [Governance](https://modelcontextprotocol.io/community/governance) and
  [SEP process](https://modelcontextprotocol.io/community/sep-guidelines),
  living documents. Governance describes LF Projects stewardship and current
  contribution/licensing policy; package-specific exceptions exist.

## S02 Open Workflow Specification

- [Released v1.0.3](https://github.com/open-workflow-specification/specification/releases/tag/v1.0.3),
  2026-07-31; [DSL reference at that tag](https://github.com/open-workflow-specification/specification/blob/v1.0.3/dsl-reference.md),
  especially Document, MCP Call, Error, Extension and Endpoint sections.
  [Repository](https://github.com/open-workflow-specification/specification) is the
  destination of the former `serverlessworkflow/specification` URL. Tagged text
  still contains older project URLs; don't rewrite error identities based on a rename.
- [Schema](https://github.com/open-workflow-specification/specification/blob/v1.0.3/schema/workflow.yaml),
  [MCP example](https://github.com/open-workflow-specification/specification/blob/v1.0.3/examples/call-mcp.yaml),
  [CTK](https://github.com/open-workflow-specification/specification/tree/v1.0.3/ctk),
  [call scenarios](https://github.com/open-workflow-specification/specification/blob/v1.0.3/ctk/features/call.feature).
  Schema MCP section and example were read from tagged raw source after the
  GitHub web reader failed on the example. The reference marks protocol version
  required; schema requires method/transport and the example omits the version.
- [Pinned Java SDK README](https://github.com/open-workflow-specification/sdk-java/blob/c481ddb4d42dc068343542ebeaa158d399b694b4/README.md)
  lists 7.x against spec 1.0.0 and includes a reference runtime;
  [Synapse](https://github.com/serverlessworkflow/synapse/tree/ba3fbfd5125995bba9fb5900aed181a0775d538c)
  is a separate runtime candidate. Neither is demonstrated here to pass an MCP
  1.0.3 interoperability profile. Repository governance/license files are available.

## S03 CWL

- [CWL Workflow description 1.2.1](https://www.commonwl.org/v1.2/Workflow.html)
  and [CommandLineTool description](https://www.commonwl.org/v1.2/CommandLineTool.html).
  Original 1.2 approval: 2020-08-07. The documents describe 1.2.1 clarifications
  and added tests while retaining `cwlVersion: v1.2`. Landing page wording still
  says 1.2.0; use the versioned documents and test version explicitly.
- [Released specification/test repository](https://github.com/common-workflow-language/cwl-v1.2/tree/551d58d409ef2a0fa2e3ab93b85167dd7d4b1833),
  [cwltool](https://github.com/common-workflow-language/cwltool/tree/490c76c56ccccdd4194040dc0cf001fafb22d099),
  [implementation list](https://www.commonwl.org/implementations/),
  [governance](https://www.commonwl.org/governance/).
  Implementation list and governance are living pages; listings are not new test results.

## S04 BPMN and DMN

- [BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2), January 2014 adoption;
  [normative PDF](https://www.omg.org/spec/BPMN/2.0.2/PDF), formal/2013-12-09.
  Clauses 2, 7.7, 10 and 13 cover conformance, extension and process semantics.
  The landing page supplies normative XSD/CMOF and informative examples.
- [OMG MIWG test suite](https://github.com/bpmn-miwg/bpmn-miwg-test-suite/tree/121a0a5d6798233ee3ca09fba778e1ecc185ea14),
  [bpmn-moddle](https://github.com/bpmn-io/bpmn-moddle) (unpinned read/write library),
  [Camunda 8.9 service task documentation](https://docs.camunda.io/docs/components/modeler/bpmn/service-tasks/)
  (page displays 8.9), [Flowable supported constructs/extensions](https://www.flowable.com/open-source/docs/bpmn/ch07b-BPMN-Constructs/)
  (living, unpinned implementation documentation).
- [DMN 1.5 formal](https://www.omg.org/spec/DMN/1.5), August 2024;
  [version index](https://www.omg.org/spec/DMN/) also lists 1.6/1.7 beta.
  [DMN TCK](https://github.com/dmn-tck/tck/tree/20274cd2ba9cad805db6114f331c743f4b2603a1)
  and [published results](https://dmn-tck.github.io/tck/) distinguish individual
  engines and cases. Do not assign every result to DMN 1.5 without checking it.

## S05 SysML, KerML and APIs

- [SysML 2.0](https://www.omg.org/spec/SysML/2.0),
  [Language PDF](https://www.omg.org/spec/SysML/2.0/Language/PDF),
  formal/2026-03-02, March 2026 document; [KerML 1.0](https://www.omg.org/spec/KerML/1.0),
  formal/26-03-01. OMG adoption history dates and final document IDs differ;
  the document IDs identify the texts reviewed.
- [Systems Modeling API 1.0](https://www.omg.org/spec/SystemsModelingAPI/1.0),
  [PDF](https://www.omg.org/spec/SystemsModelingAPI/1.0/PDF), formal/2026-03-04,
  March 2026. Project/commit services and conformance scenarios are explicit.
  OMG pages publish machine-readable schemas, interchange metadata and libraries.
- [Pilot source](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/tree/287bd59befe4971eb24bc33c1c46361a0ea14005),
  [2026-07 pilot release](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/releases/tag/2026-07)
  published 2026-08-20; [API pilot](https://github.com/Systems-Modeling/SysML-v2-API-Services/tree/0af711b14bbcea7b240bb0a3a65817ae68302092).
  Pilot implementations are not evidence of broad independent executor conformance.

## S06 STEP and manufacturing geometry

- [ISO 10303-242:2025](https://www.iso.org/standard/84300.html), edition 4,
  2025-08; [ISO 10303-238:2022](https://www.iso.org/standard/84898.html),
  edition 3, 2022-09. Catalog/abstract access only for normative ISO texts.
  AP238's catalog identifies a revision in development; a public fourth-edition
  editor's draft is not treated here as the published baseline.
- [NIST STEP File Analyzer and Viewer](https://www.nist.gov/services-resources/software/step-file-analyzer-and-viewer),
  page updated 2025-12-31, displays 5.41 and directs new releases to GitHub;
  [2021 user guide publication](https://www.nist.gov/publications/step-file-analyzer-and-viewer-user-guide-update-7).
  [STEPcode](https://github.com/stepcode/stepcode), README labels v0.8;
  [STEP Tools v17 release notes](https://www.steptools.com/docs/relnotes/relnotes-v17.html);
  [official Mastercam STEP-NC integration](https://github.com/steptools/mastercam-stepnc/blob/master/README.md)
  is a historical implementation requiring Mastercam X8 SDK, not a current plug-and-play claim.
- [CAx implementor group](https://www.mbx-if.org/home/cax/implementor-group/),
  [recommended practices](https://www.mbx-if.org/home/cax/recpractices/): General
  Testing 2.1 (2024-06-24), Geometric/Assembly Validation Properties 4.6
  (2023-04-21), Persistent IDs 1.8 (2026-03-13), Cross-Domain Exchange 1.0
  (2026-01-29) with linked STEP/QIF test files. Versions verified at index;
  detailed prescriptions inside those downloads are not asserted here.

## S07 ISA-95, B2MML and AutomationML

- [ISA official index](https://www.isa.org/standards-and-publications/isa-standards/find-isa-standards-by-topic):
  ISA-95 Part 1:2025; Parts 2/4/5:2018; Part 3:2013; Part 6:2014.
  [ISA Part 5 preview](https://www.isa.org/getmedia/bbc0eb3e-d047-440d-88fc-642b14bd8d40/ISA-95-00-05-2018-preview.pdf)
  is not the full standard. Whole-family “latest version” is inappropriate.
- [MESA B2MML/BatchML repository](https://github.com/MESAInternational/B2MML-BatchML/tree/65cc66534343c86a1ce953561e121f906a0a0cbe),
  [V7.00.00 release](https://github.com/MESAInternational/B2MML-BatchML/releases/tag/V7.00.00).
  Release notes tie v7 to the 2018 Part 2/4 changes; exact release year was not
  exposed in the rendered release page. README explicitly says its generated
  B2MML-JSON schema has not been checked/tested. XSDs and examples were located.
- [IEC 62714-1:2018](https://webstore.iec.ch/en/publication/32339), edition 2,
  2018-04-30; normative text paywalled. [AutomationML specifications index](https://www.automationml.org/about-automationml/specifications/)
  separately offers whitepapers, versioned libraries, application recommendations,
  and container guidance. [Aml.Engine](https://github.com/AutomationML/AMLEngine2.1/tree/098106acd50ca74c10a12d2cbecdae047c1f9b4b)
  is a .NET API supporting CAEX 3.0 and 2.15; its name is not an IEC edition number.

## S08 QIF

- [QIF overview](https://qifstandards.org/about-qif/),
  [ISO 23952:2020](https://www.iso.org/standard/77461.html), edition 1,
  2020-07; catalog shows confirmation in June 2026. Full ISO text not accessed.
- [QIF 3 community bindings and samples](https://github.com/QualityInformationFramework/qif-community/tree/64268c175a3058d09db29c14869b94b781518709),
  [validation tools](https://github.com/QualityInformationFramework/qif-validation-tools/tree/39843e5cc696c21ce0f8b20537d01893198f3854).
  These distinguish schema checks and additional XSLT checks.
  [DMSC's QIF 4 development presentation hosted by NIST](https://www.nist.gov/document/mbe-summit-2024-qif-kramerqif40)
  identifies member development access; no QIF 4 normative claims are made.

## S09 A2A and OPC UA

- [A2A specification](https://a2a-protocol.org/latest/specification/) (living
  generated page), [v1.0.1 release](https://github.com/a2aproject/A2A/releases/tag/v1.0.1),
  2026-05-28, [pinned repository](https://github.com/a2aproject/A2A/tree/98853be376c88df25e1704771cd3ea9ef8823a96),
  [TCK](https://github.com/a2aproject/a2a-tck) (unpinned). Do not infer the TCK
  tests every latest optional binding or replaces workflow conformance.
- [OPC UA Part 4 services](https://reference.opcfoundation.org/Core/Part4/v105/docs/)
  and [StatusCode section](https://reference.opcfoundation.org/Core/Part4/v105/docs/7.38),
  requested 1.05-series pages redirect to living OPC-10000-4 pages; exact patch
  publication not established. [Foundation .NET stack](https://github.com/OPCFoundation/UA-.NETStandard/tree/1af191ec268a85c260a56d5bc65cd96d6bac42fa),
  [CTT access page](https://opcfoundation.org/developer-tools/certification-test-tools/opc-ua-compliance-test-tool-uactt/)
  marks corporate-member access. CTT binaries/cases were not obtained.

## S10 Packaging, provenance and dependencies

- [RO-Crate 1.2](https://www.researchobject.org/ro-crate/specification/1.2/),
  community Recommendation, 2025-06-04;
  [data entities](https://www.researchobject.org/ro-crate/specification/1.2/data-entities.html),
  [Workflow Run RO-Crate profiles](https://www.researchobject.org/workflow-run-crate/),
  [ro-crate-py](https://github.com/ResearchObject/ro-crate-py),
  [rocrate-validator](https://github.com/crs4/rocrate-validator).
  Implementation/profile landing pages are unpinned; select their exact supported
  profile versions before a bake-off.
- [W3C PROV overview](https://www.w3.org/TR/prov-overview/), 2013-04-30 Note,
  distinguishes the PROV family, including normative Recommendations, from
  the overview itself. [OCI manifest](https://specs.opencontainers.org/image-spec/manifest/)
  is a living distribution reference; no OCI artifact profile is selected here.
- [Python dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
  and [platform compatibility tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/)
  are maintained specifications. Their Python-specific rules are precedents,
  not automatically portable CAD dependency semantics.

## S11 Schema, units and error formats

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12),
  [official Test Suite](https://github.com/json-schema-org/JSON-Schema-Test-Suite).
  Tests are unpinned here; no claim of complete JSON Schema conformance by Wright.
- [UCUM 2.2](https://ucum.org/ucum), 2024-06-17, including full/limited
  conformance and [official resources](https://github.com/ucum-org/ucum).
  A unit encoding is not a complete quantity/uncertainty or engineering model.
- [RFC 9457](https://datatracker.ietf.org/doc/html/rfc9457), July 2023,
  supersedes RFC 7807 for HTTP problem details. It is not the MCP wire error format.

## S12 Additional boundaries

- [FMI 3.0.2](https://fmi-standard.org/) and [SSP 2.0.1](https://ssp-standard.org/):
  published versions displayed on official sites; exact publication days not
  captured. [Reference FMUs](https://github.com/modelica/Reference-FMUs) provide
  implementation/testing assets; no simulation interoperability run performed.
- [AAS release 26-01](https://industrialdigitaltwin.org/en/content-hub/aasspecifications),
  [BaSyx Python SDK](https://github.com/eclipse-basyx/basyx-python-sdk) explicitly
  lists metamodel 3.1.2, API 3.1.1 and AASX 3.1 support, plus a compliance tool.
  These are documentation claims, with code version unpinned here.
- [SCXML](https://www.w3.org/TR/scxml/), W3C Recommendation 2015-09-01;
  [Apache Commons SCXML](https://commons.apache.org/proper/commons-scxml/).
  Unpinned implementation; not selected for first-stage work.

## S13 Adoption, governance and licensing

- [CWL governance](https://www.commonwl.org/governance/),
  [MCP governance](https://modelcontextprotocol.io/community/governance),
  [OWS governance](https://github.com/open-workflow-specification/specification/blob/2dd2c84170d5f3e05d58e913e9ca298dcf8d543a/GOVERNANCE.md),
  [OMG process](https://www.omg.org/gettingstarted/processintro.htm),
  [ISO development stages](https://www.iso.org/stages-and-resources-for-standards-development.html).
- [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0), January 2004;
  [CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode);
  [W3C Patent Policy](https://www.w3.org/policies/patent-policy/) (living policy).
  Sources for comparing options, not legal clearance or adopted project terms.

## Reproducible repository observations

Full SHA-1 Git object identities below were returned by GitHub. Dates are commit
dates, not specification publication dates. All repositories were reported
`archived: false`. Licenses must be read per artifact; GitHub's `NOASSERTION` or
missing license classification does not grant rights or prove absence of terms.

| Repository | Observed commit | Commit date (UTC) |
|---|---|---|
| modelcontextprotocol/modelcontextprotocol | `e76e9c572c6f2bfcb730357101acc90f2f802e02` | 2026-09-04 |
| modelcontextprotocol/conformance | `a983ba93c91e0bb31d0b6849eeb52f0ad1083107` | 2026-09-07 |
| modelcontextprotocol/registry | `739b70e8bc1bea203c5a35ab699f1df51d091568` | 2026-09-05 |
| modelcontextprotocol/typescript-sdk | `5119ee7fd7790e335a3fb60ef36f85334e2a6326` | 2026-09-03 |
| modelcontextprotocol/python-sdk | `9972c21aa42054fb1450c5fc614761ed11847ec6` | 2026-09-07 |
| modelcontextprotocol/inspector | `793d103db2538e1e8cf7e2eebee6330eeb51a02f` | 2026-09-02 |
| common-workflow-language/cwl-v1.2 | `551d58d409ef2a0fa2e3ab93b85167dd7d4b1833` | 2026-03-21 |
| common-workflow-language/cwltool | `490c76c56ccccdd4194040dc0cf001fafb22d099` | 2026-09-07 |
| bpmn-miwg/bpmn-miwg-test-suite | `121a0a5d6798233ee3ca09fba778e1ecc185ea14` | 2026-09-06 |
| dmn-tck/tck | `20274cd2ba9cad805db6114f331c743f4b2603a1` | 2026-08-03 |
| Systems-Modeling/SysML-v2-Pilot-Implementation | `287bd59befe4971eb24bc33c1c46361a0ea14005` | 2026-09-05 |
| Systems-Modeling/SysML-v2-API-Services | `0af711b14bbcea7b240bb0a3a65817ae68302092` | 2026-05-14 |
| MESAInternational/B2MML-BatchML | `65cc66534343c86a1ce953561e121f906a0a0cbe` | 2023-07-11 |
| AutomationML/AMLEngine2.1 | `098106acd50ca74c10a12d2cbecdae047c1f9b4b` | 2025-03-02 |
| QualityInformationFramework/qif-community | `64268c175a3058d09db29c14869b94b781518709` | 2026-03-20 |
| QualityInformationFramework/qif-validation-tools | `39843e5cc696c21ce0f8b20537d01893198f3854` | 2021-08-16 |
| open-workflow-specification/specification | `2dd2c84170d5f3e05d58e913e9ca298dcf8d543a` | 2026-08-13 |
| open-workflow-specification/sdk-java | `c481ddb4d42dc068343542ebeaa158d399b694b4` | 2026-09-07 |
| open-workflow-specification/sdk-typescript | `122bb442a0880ce10e28c4d7c5902880846ebba5` | 2026-09-03 |
| open-workflow-specification/sdk-python | `ab7b6d4d6998be2add8af7494faadd2bb16d1e94` | 2025-11-04 |
| serverlessworkflow/synapse | `ba3fbfd5125995bba9fb5900aed181a0775d538c` | 2026-03-08 |
| a2aproject/A2A | `98853be376c88df25e1704771cd3ea9ef8823a96` | 2026-09-01 |
| OPCFoundation/UA-.NETStandard | `1af191ec268a85c260a56d5bc65cd96d6bac42fa` | 2026-09-07 |

## Access and confidence ledger

| Source or check | Actual access | Consequence |
|---|---|---|
| ISO AP242/AP238/QIF, IEC 62714, full ISA-95 | Catalog abstracts / publisher descriptions / limited previews; full normative texts not obtained | Scope and available artifacts can be compared. Clause-level completeness, IP rights and conformance cannot be inferred. |
| OMG BPMN, SysML Language, Systems Modeling API | Public PDFs retrieved and relevant sections inspected | Distinguish normative requirements from pilot implementation. Initial SysML `/2.0/PDF` URL failed; correct `/2.0/Language/PDF` succeeded. |
| MCP registry and SysML pilot files | Initial guessed `.md` paths returned 404; repository tree supplied correct paths, then direct raw reads succeeded | Recovered access, not an inaccessible standard. Only corrected paths are cited. |
| MCP `/basic/versioning` and `/registry/server-json` web routes | Web reader failed | Version-change claims use retrieved changelog; registry claims use pinned official source files. |
| MESA original brief link | Web reader error | Official MESA GitHub repository and ISA sources used instead. |
| STEP Tools product landing page | Web reader error | Official versioned release notes and integration repository used; current commercial feature breadth not established. |
| OPC CTT / QIF member development | Restricted access; no private artifacts retrieved | Existence/access model is documented; test coverage and unpublished normative content remain unknown. |
| Public GitHub metadata | Successful for table above, then unauthenticated rate limit reached | Extra library links remain unpinned; no invented commits or release dates. |
| Wright and external interoperability | Read-only source/record inspection; no new execution | Proposed test matrix is unexecuted. Recorded CAD evidence is narrowly scoped and not independent conformance. |
