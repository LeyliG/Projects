This folder contains code and files utilized as part of the Pre-Post LLMs for Code Era. 

Step 1: Use the SEART (GHS) data to identify candidate projects for manual analysis. <br>
  Inputs:  <br>
  Outputs:  <br>


Step 2: Run scripts to mine the software repositories for mention of "Copilot" and perform manual analysis to confirm proper usage of copilot by the repositories. <br>
  Input: List of candidate projetcs. <br>
  Output: List of confirmed projects that have confirmed usage of Copilot at some point in their history. <br>


Step 3: Use the list of projects with confirmed usage of Copilot to collect the aggregated monthly data on the metrics of interest. <br>
  Input: List of Copilot user project. <br>
  Output: Monthly aggregated data. <br>
 

Step 4: Using the monthly data fit the Interrupted Time Series Mixed-Effects model. <br>
  Input: Monthly aggregated data. <br>
  Output: Model results.


