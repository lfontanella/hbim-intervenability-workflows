# HBIM Intervenability Workflows

This repository contains HBIM/BIM workflows developed to assess the intervenability of existing and heritage buildings through Revit, Dynamo, Python and Excel-based constraint processing.

The workflow was developed as part of a PhD research project on BIM, HBIM, openBIM standards and digital procedures for supporting analysis, monitoring and decision-making in heritage and existing building contexts.

## Research context

The repository documents a workflow for evaluating the feasibility and relative invasiveness of possible interventions on existing building components.

In heritage and existing buildings, design decisions are not only related to technical performance, but also to constraints connected with:

- material conservation;
- reversibility of interventions;
- geometric and constructive limitations;
- possibility of perforation, demolition, bonding or infill;
- accessibility and walkability of spaces;
- admissible intervention depth, width or diameter;
- compatibility between design actions and existing elements.

The workflow aims to support decision-making by translating these constraints into structured parameters, computational rules and visual outputs in the BIM model.

## Repository structure

```text
hbim-intervenability-workflows/
│
├── README.md
├── CITATION.cff
├── LICENSE
├── .gitignore
│
├── START.json
├── START - AdD - Dynamo.json
│
├── python/
│   └── Intervenability_01-LFO.py
│
├── dynamo/
│   └── Intervenability_02-LFO.dyn
│
├── parameters/
│   └── SharedParameter_Intervenibility.txt
│
├── AdD_Dynamo/
│   ├── IN/
│   │   └── InputDataLFO.xlsx
│   └── OUT/
│       └── Intervenability_RESULTS.xlsx
│
├── images/
│   ├── revit-dynamo-intervenability-visualization.jpg
│   ├── hbim-case-study-section-reference.jpg
│   ├── hbim-intervenability-model-output.jpg
│   ├── intervenability-openbim-workflow-diagram.jpg
│   ├── intervenability-revit-dynamo-workflow-diagram.jpg
│   └── revit-shared-parameters-intervenability.jpg
│
└── video/
    └── Intervenibility.mp4
```

## Workflow overview

The workflow is based on the following logic:

```text
Revit / HBIM model
        ↓
shared parameters describing intervention constraints
        ↓
Dynamo extraction of element parameters
        ↓
Excel input file with queries, elements, constraints and settings
        ↓
external Python script
        ↓
intervenability and feasibility calculation
        ↓
Excel output file with results
        ↓
Dynamo reads results
        ↓
BIM elements are coloured according to intervenability values
```

## Main components

### Revit shared parameters

The file:

```text
parameters/SharedParameter_Intervenibility.txt
```

contains shared parameters used to describe intervention-related constraints on building elements.

Examples include parameters related to:

- bonding;
- leaning;
- demolition;
- infill;
- excavation;
- cut-out depth and width;
- perforation dimensions and positions;
- through-hole dimensions;
- attic accessibility and walkability;
- use as duct space;
- surface covering level.

These parameters are used to describe the possible or admissible intervention actions on existing building components.

### Dynamo workflow

The Dynamo file:

```text
dynamo/Intervenability_02-LFO.dyn
```

is used to:

1. read selected Revit element parameters;
2. export model data to the Excel input file;
3. run the external Python script;
4. read the resulting intervenability values;
5. apply colour overrides to elements in the active Revit view.

The Dynamo graph acts as a bridge between the Revit model, the Excel input/output files and the Python calculation script.

### Python calculation script

The Python file:

```text
python/Intervenability_01-LFO.py
```

performs the intervenability calculation.

The script reads:

```text
AdD_Dynamo/IN/InputDataLFO.xlsx
```

and processes the sheets containing:

- queries;
- element data;
- intervention constraints;
- settings.

It then generates:

```text
AdD_Dynamo/OUT/Intervenability_RESULTS.xlsx
```

The output file contains:

- a `SUMMARY` sheet with the intervenability result and colour values for each element;
- a `DETAILS` sheet with intervention-by-intervention feasibility results.

### Excel input and output

The Excel input file:

```text
AdD_Dynamo/IN/InputDataLFO.xlsx
```

contains the structured information required by the workflow.

The Excel output file:

```text
AdD_Dynamo/OUT/Intervenability_RESULTS.xlsx
```

contains the computed results produced by the Python script and read back by Dynamo.

The Excel files are included because they are part of the documented research workflow.

### Configuration files

The configuration files:

```text
START.json
START - AdD - Dynamo.json
```

define the workflow configuration, including the input folder, output folder, input file name and Excel sheet names.

These files allow the Python script and the Dynamo workflow to operate using a defined project structure.

### Images

The `images` folder contains figures documenting the workflow, including:

- Revit/Dynamo model visualization;
- shared parameter configuration;
- HBIM model outputs;
- workflow diagrams;
- comparison between model output and case-study reference images.

### Video

The video:

```text
video/Intervenibility.mp4
```

documents the workflow execution and visual output.

The video is included because it represents an essential part of the research documentation.

## Role in the research workflow

This repository documents the part of the research related to intervenability assessment in existing and heritage building contexts.

The workflow demonstrates how BIM/HBIM models can be enriched with intervention-related constraints and then processed to support decision-making.

The aim is to move from a purely geometric or descriptive model toward a model capable of supporting questions such as:

- Which interventions are feasible on a given element?
- Which elements are more or less intervenable?
- Which interventions are more invasive?
- Which parts of the building present stronger constraints?
- How can intervenability information be visualized directly in the BIM model?

## OpenBIM and proprietary workflow logic

The repository includes a Revit/Dynamo-based implementation, but the methodology is connected to broader openBIM research questions.

The workflow explores how information requirements, constraints and feasibility rules can be structured, processed and visualized in relation to BIM/HBIM elements.

The included diagrams document both:

- a Revit/Dynamo implementation workflow;
- an openBIM-oriented conceptual workflow based on IFC, structured constraints and external processing.

## Data and publication note

This repository intentionally does not include the original Revit model or confidential building files.

The repository includes:

- scripts;
- Dynamo workflow;
- shared parameter file;
- Excel input/output files used to document the procedure;
- images;
- video documentation.

Before reuse, users should adapt paths, model parameters, element categories and constraint values to their own project.

## Limitations

This repository documents a research prototype.

It is not intended as:

- a certified conservation assessment tool;
- a production-ready facility management platform;
- an automatic design approval system;
- a substitute for professional heritage assessment;
- a substitute for conservation expertise.

The workflow should be interpreted as a methodological prototype for structuring, processing and visualizing intervenability constraints in BIM/HBIM environments.

## Citation

If you use or refer to this repository, please cite the related PhD thesis and this repository.

Suggested citation:

Fontanella, L. (2026). *HBIM Intervenability Workflows: Revit, Dynamo, Python and Excel-based procedures for assessing intervention feasibility in existing and heritage buildings*. GitHub repository.

## Author

Luca Fontanella  
Università Iuav di Venezia  
PhD programme: Culture del progetto
