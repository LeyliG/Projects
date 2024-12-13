This folder contains code and files utilized as part of the Pre-Post LLMs for Code Era. 

### Step 1: Use the SEART (GHS) data to identify candidate projects for manual analysis. <br>
  > **Python Files:** ```ghs_data_process.py``` <br>
  > **Inputs:** GHS files stored in the data_files folder: ```ghs_c_plus_plus.csv, ghs_c_sharp.csv, ghs_go.csv , ghs_java.csv, ghs_python.csv, ghs_ruby.csv, ghs_typescript.csv, ghs_javascript.csv``` <br>
  > **Outputs:** ```'./data_files/gh_popular_repo_data.csv'``` file containing names of the repositories for mining and manual analysis. <br>


### Step 2: Run scripts to mine the software repositories for mention of "Copilot" and perform manual analysis to confirm proper usage of copilot by the repositories. <br>
  > **Python Files:**  <br>
  > **Input:** List of candidate projetcs (output of step 1). <br>
  > **Output:** List of confirmed projects that have confirmed usage of Copilot at some point in their history. <br>


### Step 3: Use the list of projects with confirmed usage of Copilot to collect the aggregated monthly data on the metrics of interest. <br>
  > **Python Files:**  <br>
  > **Input:** List of Copilot user project. <br>
  > **Output:** Monthly aggregated data. <br>
 


### Step 4: Using the monthly data fit the Interrupted Time Series Mixed-Effects model. <br>
  > **Python Files:**  <br>
  > **Input:** Monthly aggregated data. <br>
  > **Output:** Model results.




