'''
Author: Leyli (Aya) Garryyeva

Fits mixed-effects models for multiple dependent variables:
  - unique_authors
  - merge_commits
  - non_merge_commits
  - mean_commit_churn
Uses fixed effects (time_12, copilot, time_since_copilot)
Includes random effects for repository and mainLanguage
Generates diagnostic plots and R-squared values
Collects results in a DataFrame

'''


import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import datetime as Dt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import statsmodels.formula.api as smf
from pymer4.models import Lmer
import researchpy as rp
import scipy.stats as stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
# Scaling techniques
from sklearn.preprocessing import (
    MaxAbsScaler, MinMaxScaler, Normalizer, PowerTransformer,
    QuantileTransformer, RobustScaler, StandardScaler, SplineTransformer
)
from gh_time_series_data_prep import preprocess_data

# Define functions:
# R^2 and plot functions for QQ-plot and Residuals vs. Fitted values
def plot_model_diagnostics(result, y_var, x_obs_var):
    """
    Create diagnostic plots for mixed-effects model:
    1. QQ-plot of residuals
    2. Residuals vs. Fitted values plot
    
    Parameters:
    -----------
    result : statsmodels MixedLM fit result
    y_var : str, dependent variable name
    x_obs_var : str, observation variable name
    """
    # Compute residuals
    residuals = result.resid
    fitted_values = result.fittedvalues
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 1. QQ-Plot
    # Theoretical quantiles
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(residuals)))
    
    # Sort residuals
    sorted_residuals = np.sort(residuals)
    
    # Plot QQ-Plot
    ax1.scatter(theoretical_quantiles, sorted_residuals, alpha=0.7)
    ax1.plot(theoretical_quantiles, theoretical_quantiles, color='red', linestyle='--')
    ax1.set_title(f'QQ-Plot of Residuals\n{y_var} ~ {x_obs_var}')
    ax1.set_xlabel('Theoretical Quantiles')
    ax1.set_ylabel('Sample Quantiles')
    
    # 2. Residuals vs. Fitted Values Plot
    ax2.scatter(fitted_values, residuals, alpha=0.7)
    ax2.axhline(y=0, color='red', linestyle='--')
    ax2.set_title(f'Residuals vs. Fitted Values\n{y_var} ~ {x_obs_var}')
    ax2.set_xlabel('Fitted Values')
    ax2.set_ylabel('Residuals')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(f'model_diagnostics_{y_var}_{x_obs_var}.png')
    plt.show()
    plt.close() # Close the plot to free up memory


def calculate_r_squared_mixed(result):
    """
    Calculate marginal and conditional R-squared for mixed-effects models
    
    Parameters:
    -----------
    result : statsmodels MixedLM fit result
    
    Returns:
    --------
    tuple: (marginal_r_squared, conditional_r_squared)
    """
    try:
        # Total variance of the response variable
        total_var = np.var(result.model.endog)
        
        # Variance of fixed effects predictions
        fixed_effects = result.fittedvalues
        var_fixed = np.var(fixed_effects)
        
        # Residual variance
        var_resid = result.scale
        
        # Check if random effects exist
        if hasattr(result, 'random_effects') and result.random_effects:
            # Calculate random effects variance
            random_effect_values = list(result.random_effects.values())
            var_random = np.var([re[0] for re in random_effect_values if len(re) > 0])
        else:
            var_random = 0
        
        # Marginal R-squared (variance explained by fixed effects)
        marginal_r_squared = 1 - (var_resid / total_var)
        
        # Conditional R-squared (variance explained by fixed and random effects)
        conditional_r_squared = 1 - ((var_resid + var_random) / total_var)
        
        return marginal_r_squared, conditional_r_squared
    
    except Exception as e:
        print(f"Error calculating R-squared: {e}")
        return np.nan, np.nan



# Fit Mixed-Effects Regression Model
# Call the function and get the filtered data
filtered_data = preprocess_data()

# get a list of numeric columns in monhtly_commits 
numeric_columns = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
# Exclude 'intervention' and 'month_index' from numeric columns
columns_to_exclude = ['copilot', 'month_index']
numeric_columns = [col for col in numeric_columns if col not in columns_to_exclude]

# scale the numeric features
scaler = StandardScaler()

scaled_df = filtered_df.copy()
scaled_df[numeric_columns] = scaler.fit_transform(scaled_df[numeric_columns])

# remove rows with month_index == 0
scaled_df = scaled_df[scaled_df['month_index'] != 0]

# check variance inflation factor
# Create a DataFrame that will contain the names of all the feature variables and their respective VIFs
vif_data = pd.DataFrame()
vif_data["feature"] = ["time_12", "time_since_copilot", "repo_age_2021", "commits"]

# Calculate the VIFs for each feature and store in the DataFrame
vif_data["VIF"] = [variance_inflation_factor(scaled_df[["time_12", "time_since_copilot", "repo_age_2021", "commits"]].values, i)
                   for i in range(len(vif_data["feature"]) )]
print(vif_data)

# Define variables
y_vars = ['unique_authors', 'merge_commits', 
          'non_merge_commits', 'mean_commit_churn'
          #, 'blank_lines', 'code_lines', 'comment_lines'
          ]
confounders = ['repo_age_2021', 'commits']
random_effects = ['repository', 'mainLanguage']
intervention_vars = ['time_12', 'copilot', 'time_since_copilot']

# Fit the mixed-effects model: nested data {mainLanguage, repository}
import statsmodels.formula.api as smf
import scipy.stats as stats

# Modified model fitting loop
x_obs_vars = ['time_12'] # time_24
model_results = []

for y_var in y_vars:
    for x_obs_var in x_obs_vars:
        # Basic model
        formula = f"{y_var} ~ time_12 + C(copilot) + time_since_copilot  + repo_age_2021 + commits"
        print(f"Fitting model for {y_var}...")
        
        # Fit the mixed-effects model
        model = smf.mixedlm(
            formula=formula,
            data=scaled_df,
            groups=scaled_df["repository"],  # Random intercepts for mainLanguage
            re_formula="1", # Random intercepts for repositories
            vc_formula={'mainLanguage': '1' } # Random intercepts for repositories
        )
        
        # Fit the model
        result = model.fit(
            # optimizer params: need these to be able to add re_formula for random intercepts in groups
            method= 'bfgs', #'lbfgs',  #  'bfgs'
            maxiter=1000,
            ftol=1e-8
        )
        
        # Calculate R-squared
        marginal_r2, conditional_r2 = calculate_r_squared_mixed(result)
        
        # Create diagnostic plots
        plot_model_diagnostics(result, y_var, x_obs_var)
        
        # Print model summary and R-squared
        print(result.summary())
        
        # Safely print R-squared values
        print(f"\nMarginal R-squared: {marginal_r2 if not np.isnan(marginal_r2) else 'N/A'}")
        print(f"Conditional R-squared: {conditional_r2 if not np.isnan(conditional_r2) else 'N/A'}")
        
        

        # Collect results
        for var, coef, pval in zip(result.params.index, result.params.values, result.pvalues.values):
            model_results.append({
                'Dependent_Variable': y_var,
                'Observation_Variable': x_obs_var,
                'Independent_Variable': var,
                'Coefficient': coef,
                'P-value': pval,
                'Marginal_R_Squared': marginal_r2,
                'Conditional_R_Squared': conditional_r2,
                'Significant': pval < 0.05
            })

# Convert results to DataFrame
results_df = pd.DataFrame(model_results)

# Save and display results
#results_df.to_csv('model_results.csv', index=False)
print("\nSignificant Results:")
print(results_df[results_df['Significant']])







