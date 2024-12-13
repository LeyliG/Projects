#### This folder contains code and files utilized as part of the Pre-Post LLMs for Code Era. 


### Environment set up
```
conda create -n copilot python=3.11
conda activate copilot
conda install numpy pandas matplotlib requests ipykernel

pip install -r requirements.txt
```




-----


### Step 1: Use the SEART (GHS) data to identify candidate projects for manual analysis. <br>
  > **Python Files:** ```ghs_data_process.py``` <br>
  > **Inputs:** GHS files stored in the data_files folder: ```ghs_c_plus_plus.csv, ghs_c_sharp.csv, ghs_go.csv , ghs_java.csv, ghs_python.csv, ghs_ruby.csv, ghs_typescript.csv, ghs_javascript.csv``` <br>
  > **Outputs:** ```'./data_files/gh_popular_repo_data.csv'``` file containing names of the repositories for mining and manual analysis. <br>


### Step 2: Run scripts to mine the software repositories for mention of "Copilot" and perform manual analysis to confirm proper usage of copilot by the repositories. <br>
  > **Python Files:** ```keyword_search``` folder contains all the scripts used for this step <br>
  > **Input:** List of candidate projetcs (output of step 1). <br>
  > **Output:** List of confirmed projects that have confirmed usage of Copilot at some point in their history. <br>


### Step 3: Use the list of projects with confirmed usage of Copilot to collect the aggregated monthly data on the metrics of interest. <br>
  > **Python Files:** ```gh_monthly_commit_code.py``` <br>
  > **Other required files** ```token.txt```
  > **Input:** List of Copilot user project. In the study we have two separate lists, one is the projects identified through Commits (```copilot_repos_commits.xlsx```) and the other one is from Pull Requests (```copilot_repos_prs.xlsx```) with both files stored in ```data_files``` folder. <br>
  > **Output:** Monthly aggregated data stored in ```gh_monthly_commit_data.csv```. <br>
 


### Step 4: Using the monthly data fit the Interrupted Time Series Mixed-Effects model. <br>
  > **Python Files:** ```gh_monthly_time_series_model.py``` <br>
  > **Input:** Monthly aggregated data ```gh_monthly_commit_data.csv``` and repository level data ```gh_popular_repo_data.csv```. <br>
  > **Output:** Model results in a table format including coefficients, standard error, p-value. Additionally, the outputs include the marginal and conditional R-squared values along with QQ-plot and Residuals vs Fitted values plots. 




