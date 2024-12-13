This folder contains code and files utilized as part of the Pre-Post LLMs for Code Era. 

Step 1: Use the SEART (GHS) data to identify candidate projects for manual analysis.
  Inputs:
  Outputs: 


Step 2: Run scripts to mine the software repositories for mention of "Copilot" and perform manual analysis to confirm proper usage of copilot by the repositories.
  Input: List of candidate projetcs.
  Output: List of confirmed projects that have confirmed usage of Copilot at some point in their history.


Step 3: Use the list of projects with confirmed usage of Copilot to collect the aggregated monthly data on the metrics of interest.
  Input: List of Copilot user project.
  Output: Monthly aggregated data. 


Step 4: Using the monthly data fit the Interrupted Time Series Mixed-Effects model.
  Input: Monthly aggregated data.
  Output: Model results.


