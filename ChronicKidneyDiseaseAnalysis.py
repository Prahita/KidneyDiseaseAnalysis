# -*- coding: utf-8 -*-
"""Final Project part 5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TNkkwA-GiPfNR1V0Ip6rDPEenY_ZNhnP

# Group Final Project

Dataset: Chronic Kidney Disease from Kaggle.com

Coding by: Prahita Magal, Emily Miyashiro, Jessica Miyasato

# NOTE: Results may vary from out intial conclusion because we had to rerun the code for the pdf version

## Differences since Analysis Plan part 3:
*   We had to make sure not to use categorical variables in the clustering models because they cannot assess categorical variables
*   We had switch the order of coding for the questions so that the code block would run so now question 1 is question 2 and question 2 is now question one
* What is now question one, was changed from the initial analysis plan since it was too similar to question 4.
*   The current question 1 in this coding had to be changed because it was too similar to question 4
*   We had to figured out how to find the hyperparameters for some of the model because we previously did not have that
*   For question 6, we put a LASSO and Logistic Regression comparison to show the change in coeffients. Also a LASSO penalty was added to the Logistic Regression to find the most impactful variable.
* We had to add a scree plot for question 2 because I forgot to put two graphs in my analysis plan 
* We also did'nt include the categorical variables for question 2 because we are running a PCA model. 
* We added a confusion matrix for question 4 because I forgot to put two graphs in my analysis plan.
* We slightly changed question 4 by combining the old question 2 and question 4 because they were similar.
"""

# Commented out IPython magic to ensure Python compatibility.
import warnings
warnings.filterwarnings('ignore')


import pandas as pd
import numpy as np
from plotnine import *

from sklearn.neighbors import KNeighborsClassifier

from sklearn.decomposition import PCA

from sklearn import metrics 
from sklearn.preprocessing import StandardScaler #Z-score variables

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error #model evaluation

from sklearn.linear_model import LogisticRegression

from sklearn.tree import DecisionTreeClassifier # Decision Tree

from sklearn.model_selection import train_test_split # simple TT split cv
from sklearn.model_selection import KFold # k-fold cv
from sklearn.model_selection import LeaveOneOut #LOO cv
from sklearn.model_selection import cross_val_score # cross validation metrics
from sklearn.model_selection import cross_val_predict # cross validation metrics

from sklearn.metrics import accuracy_score, confusion_matrix,precision_score
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import f1_score, recall_score, plot_roc_curve, precision_score, roc_auc_score

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer

from mizani.utils import precision

from sklearn.cluster import AgglomerativeClustering

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression

from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

from sklearn.metrics import silhouette_score, silhouette_samples

# make sure you have these to make dendrograms!-------
import scipy.cluster.hierarchy as sch
from matplotlib import pyplot as plt

# %matplotlib inline
from google.colab import drive 

from sklearn import datasets
from sklearn.tree import DecisionTreeRegressor
from sklearn import tree

from sklearn.linear_model import RidgeCV, LassoCV

# giving colab acess to drive files in order to import dataset

drive.mount('/content/gdrive')

df_train = pd.read_csv('gdrive/My Drive/kidney_disease_train.csv')
df_test = pd.read_csv('gdrive/My Drive/kidney_disease_test.csv')

print(df_train.shape)
print(df_test.shape)

"""#Cleaning and Combining Data

"""

# Combining two datasets into one for our clustering models 

frames = [df_train,df_test]

combined_df = pd.concat(frames)

# new combined dataset for our clustering models or just in case

combined_df

# Cleaning dataset 

#Removing the '?' from data set
combined_df.replace("\t?", np.nan, inplace = True)

#Calculate the average of the columns

avg_norm_loss_pcv = combined_df['pcv'].astype('float').mean(axis=0) 
avg_norm_loss_rc = combined_df['rc'].astype('float').mean(axis=0) 
avg_norm_loss_wc = combined_df['wc'].astype('float').mean(axis=0) 
    
#Replace "NaN" by mean value in 'pcv','wc','rc' columns

combined_df['pcv'].replace(np.nan, avg_norm_loss_pcv, inplace=True) 
combined_df['rc'].replace(np.nan, avg_norm_loss_rc, inplace=True) 
combined_df['wc'].replace(np.nan, avg_norm_loss_wc, inplace=True) 

# Instead of dropping all rows with NA/Nan values, for null values which are float data type we will insert in the average to retain our rows

combined_df = combined_df.fillna(combined_df.mean())


combined_df.head()

# we will turn categorical variables into dummy binary variables 

#classification - ckd/chronic kidney disease
dummy_class = pd.get_dummies(combined_df['classification'])
dummy_class.head()

# Bacteria present - ba
dummy_ba = pd.get_dummies(combined_df['ba'], prefix='bacteria', prefix_sep='.')
dummy_ba.head()

# Heart disease / coronary artery disease (cad)
dummy_cad = pd.get_dummies(combined_df['cad'], prefix='heart_disease', prefix_sep='.')
dummy_cad.head()

#Anemia - ane
dummy_ane = pd.get_dummies(combined_df['ane'], prefix='anemia', prefix_sep='.')
dummy_ane.head()

# Pedal edema - pe 
dummy_pe = pd.get_dummies(combined_df['pe'], prefix='pedaledema', prefix_sep='.')
dummy_pe.head()

# Type 2 diabetes / Diabetes - dm
dummy_dm = pd.get_dummies(combined_df['dm'], prefix='diabetes', prefix_sep='.')
dummy_dm.head()


# appetite (keep both columns) - appet
dummy_appet = pd.get_dummies(combined_df['appet'], prefix='appetite', prefix_sep='.')
dummy_appet.head()

# hypertension - htn
dummy_htn = pd.get_dummies(combined_df['htn'], prefix='hyptertension', prefix_sep='.')
dummy_htn.head()

# pus cell clumps - pcc
dummy_pcc = pd.get_dummies(combined_df['pcc'], prefix='puscellclumps', prefix_sep='.')
dummy_pcc.head()

# pus cell levels - pc
dummy_pc = pd.get_dummies(combined_df['pc'], prefix='puscell_level', prefix_sep='.')
dummy_pc.head()


combined_df = pd.concat((combined_df,dummy_class,dummy_ba,dummy_cad,dummy_ane,dummy_pe,dummy_dm,dummy_appet,dummy_htn,dummy_pcc,dummy_pc),axis=1)
combined_df = combined_df.drop(['classification','notckd','ba','bacteria.notpresent','cad','heart_disease.\tno','heart_disease.no',
                                'anemia.no','ane','pedaledema.no','pe','diabetes.\tno','diabetes.\tyes','diabetes.no','diabetes. yes','dm','hyptertension.no','htn',
                                 'puscellclumps.notpresent','pcc','puscell_level.normal','pc','appet'],
                               axis=1)

# FINAL COMBINED CLEANED DATASET
combined_df.head()

"""#**1.** For people above 50 with Chronic Kidney Disease (ckd), what are the leading predictors of determining Chronic Kidney Disease?"""

# (Supervised) For people above 50 with ckd, what are the leading predictors of determining ckd?
over50_df = combined_df.loc[combined_df['age'] >= 50]
# Using Decision Tree

predictors = ['age','bp','sg','al','su','bgr','bu','sc','sod','pot','hemo','bacteria.present','heart_disease.yes','anemia.yes','pedaledema.yes',
 'diabetes.yes','appetite.good','appetite.poor','hyptertension.yes',
 'puscellclumps.present','puscell_level.abnormal']

contin_predictors = ['age','bp','sg','al','su','bgr','bu','sc','sod','pot','hemo']

X = over50_df[predictors]
y = over50_df["ckd"]

#Z-scoring
z = StandardScaler()

X[contin_predictors] = z.fit_transform(X[contin_predictors])



# TTS
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2,random_state = 1234)

X_train.head()

# Tree model
treemod = DecisionTreeClassifier(max_depth = 7,random_state = 1234)
treemod.fit(X_train,y_train)


# confusion matrices for train and test
plot_confusion_matrix(treemod, X_test, y_test)
plot_confusion_matrix(treemod, X_train, y_train)

print("Train Acc: ", accuracy_score(y_train, treemod.predict(X_train)))
print("Test Acc: ", accuracy_score(y_test, treemod.predict(X_test)))

print("TEST Precision : ", precision_score(y_test, treemod.predict(X_test)))
print("TRAIN Precision: ", precision_score(y_train, treemod.predict(X_train)))

print("TEST Recall : ", recall_score(y_test, treemod.predict(X_test)))
print("TRAIN Recall: ", recall_score(y_train, treemod.predict(X_train)))

print("TEST ROC/AUC : ", roc_auc_score(y_test, treemod.predict_proba(X_test)[:,1]))
print("TRAIN ROC/AUC: ", roc_auc_score(y_train, treemod.predict_proba(X_train)[:,1]))

print("MSE TRAIN: ", mean_squared_error(y_train, treemod.predict(X_train)))
print("MSE TEST : ", mean_squared_error(y_test, treemod.predict(X_test)))

# Tree features, depth and leaf size

print(treemod.feature_importances_)
print("Depth size: ",treemod.get_depth())
treemod.get_n_leaves()

tree.plot_tree(treemod);

"""## Answer to Question 1: 

Looking at the feature importance, we can see that index 3,5 and 11 are the highest, signifying that they are the most important variables in determining kidney disease. These are the variables sg,su and hemo respectively; this means that the specific gravity of urine(concentration of all chemicals in your urine), the sugar level in your blood, and the hemoglobin levels in your blood are the three most significant variables in determining a kidney disease diagnosis. With hemoglobin having the largest variable importance score, we can derive that monitoring that variable in your health would be a good measure of your liklihood of getting chronic kidney disease. We can make a suggestion that patients should be viglante with monitoring their blood oxygen levels and hemoglobin levels, as cardiorenal health is directly interactive with kidney function.

**In regards to model performance:**

Looking at the metrics and the confusion plots, it is clear the model was definately overfit to the training set. However, the MSE did remain relatively lower. In order to minimize the gap between training and test set performance in the future, I would have varied the number of leaves or even lowered the maximum depth the tree would have in order to be less biased towards training set data.

#**2.** Based on the cumulative variance plot, what is the optimal number of components we should retain to achieve 75% of variance?
"""

# Based on the cumulative variance plot, what is the optimal number of components we should retain to achieve 75% of variance? 

combined_df.dtypes

f=["age","bp", "sg", "al", "su", "bgr", "bu","sc","sod", "pot","hemo"]

# z-score
zs = StandardScaler()
combined_df[f] = zs.fit_transform(combined_df[f])

# build PCA model 
pca = PCA()
pca.fit(combined_df[f])
# create dataframe with the variance, the number of components, and then the cumulative variance.
pcaDF = pd.DataFrame({"expl_var" :
                      pca.explained_variance_ratio_,
                      "pc": range(1,12),
                      "cum_var":
                      pca.explained_variance_ratio_.cumsum()})
pcaDF.head()

# create scree plot
print(ggplot(pcaDF, aes(x = "pc", y = "expl_var")) + geom_line() + geom_point())

#create cumulative variance plot
print(ggplot(pcaDF, aes(x = "pc", y = "cum_var")) + geom_line(color = "pink") +
 geom_point(color = "pink") + geom_hline(yintercept = 0.75))
pcaDF.head()

"""## Answer to Question 2: 
Based on the cumulative variance plot, we would need to keep at least 6 principal components to retain 75% of the original variance. You can tell by looking at the black horizontal line. This line represents 75% of the original variance. The point where the black horizontal line and the pink line intersects tells you how many components you would need to keep. Since the black line intersects the pink line just above the 5th point, we would need to keep the 6 components in order to keep 75% of the original variance. 

In contrast, the scree plot tells suggests that we only need to keep about 3 principal components. The scree plot tells us how many components to keep by looking at the point of inflection. This is also known as the elbow method. The point of inflection in our graph is 3. The 1st component alone explains about .35 of the explained variance of our original data. The second one explains .14 and the third component explains .1. After the 3rd component, the other component don't add a lot of information. Therefore, we would only need to keep 3 components and can disregard the rest.

#**3.** What will separation and distinction between clusters look like with the presence of different types of diseases (coronary artery disease being a heart-centered disease, etc)?
"""

# (Clustering - supervised) What will separation and distinction between clusters look like with the presence of different types of diseases ( coronary artery disease being a heart-centered disease, etc)?

# Variables Involved: cad,dm,htn,anemia,pe ( all categorical) (can’t cluster with categorical)

# Modeling/Computation: We will use a KMeans

features = ['bp','sod','pot','sc','bu','bgr']
X =  combined_df[features]

z = StandardScaler()

X[features] = z.fit_transform(X[features])

# model
km = KMeans(n_clusters = 3)
km.fit(X[features])

membership = km.predict(X[features])

X["cluster"] = membership

print(silhouette_score(X[features], membership))

membership

# Choosing appropriate K 

# SSE for K-Means
ks = [2,3,4,5,6,7,8,9,10]

sse =  []
sil = []

for k in ks:
  km = KMeans(n_clusters = k)
  km.fit(X[features])

  sse.append(km.inertia_)
  sil.append(silhouette_score(X[features], km.predict(X[features])))

sse_df = pd.DataFrame({"K": ks,
                       "sse": sse,
                       "silhouette": sil})

(ggplot(sse_df, aes(x = "K", y = "sse")) + 
 geom_line() + geom_point() +
 theme_minimal() + 
 labs(title = "SSE for Different Ks"))

# silhouette score
(ggplot(sse_df, aes(x = "K", y = "silhouette")) + 
 geom_line() + geom_point() +
 theme_minimal() + 
 labs(title = "Silhouette for Different Ks"))

# Looking at these two graphs, It appears that 5 is the optimal # of K which has a decent silhouette score and a lower SSE

km2 = KMeans(n_clusters = 5)
km2.fit(X[features])

membership2 = km2.predict(X[features])

X["cluster"] = membership2

print(silhouette_score(X[features], membership2))

sil_points = silhouette_samples(X[features], membership)

# add silhouette scores and clusters to X
X["sil"] = sil_points
X["cluster"] = membership

# sort X by cluster and silhouette score just to look better
X = X.sort_values(by = ["cluster", "sil"], ascending = True)

# number rows for graphing
X["number"] = range(0,X.shape[0])

(ggplot(X, aes(x = "number", y = "sil", fill = "factor(cluster)"))
+ geom_bar(stat = "identity") + 
 geom_hline(yintercept = np.mean(sil_points), linetype = "dashed") +
theme_minimal() + 
labs(x = "", y = "Silhouette Score", title = "Silhouette Scores") + 
theme(axis_text_x= element_blank(),
panel_grid_major_x= element_blank(),
panel_grid_minor_x= element_blank(),
legend_position= "bottom") +
scale_fill_discrete(name = "Cluster"))

# Visualizations 

print((ggplot(X, aes(x = "bu", y = "bgr", color = "factor(cluster)")) + geom_point() + 
 theme_minimal() + labs(title = "Blood Urea vs Blood Glucose Clusters")))

print((ggplot(X, aes(x = "bu", y = "bp", color = "factor(cluster)")) + geom_point() + 
 theme_minimal() + labs(title = "Blood Urea vs Blood Pressure Clusters")))

print((ggplot(X, aes(x = "bu", y = "sod", color = "factor(cluster)")) + geom_point() + 
 theme_minimal() + labs(title = "Blood Urea vs sodium Clusters")))

print((ggplot(X, aes(x = "bu", y = "pot", color = "factor(cluster)")) + geom_point() + 
 theme_minimal() + labs(title = "Blood Urea vs Potassium Clusters")))

print((ggplot(X, aes(x = "bu", y = "sc", color = "factor(cluster)")) + geom_point() + 
 theme_minimal() + labs(title = "Blood Urea vs serum creatine Clusters")))

"""## Answer to Question 3: 

Looking at the various scatteplots, we can see there are some clear clusters in some graphs which have some sort of relationship. 

In the graph that plots blood urea vs blood glucose, we can see there are three distinct groups, one with low BU and low BG, one with high BU and low BG, and one with low BU and high BG. This variation in the composition of levels of blood urea compared to blood sugar in general suggests that there is some definitive relationship between how well your body is able to regulate blood sugar and the concentration of blood urea. Both these variables in tandem have a relationship to whether or not someone is diabetic or overhydrated. Someone with low BU and high BG is diabetic, somone who falls in the cluster of low BG and high Blood Urea has some underlying kidney problem already or has a chemical imbalance in their urine. Someone with low BU and BG is most common, as it might explain the general population which is able to stay hydrated and manage their sugar levels well.

Similarily, we can look to the scatterplot on serum creatine vs blood urea level, we find two main groups, one with lower BU and serum creatine levels, and one with slightly higher BU levels and higher serum creatine levels. Serum creatine is the waste product that comes from your tissues and muscles from regular wear and tear of your body, measuring this level measures how well yout kidney is at flushing out this waste and by product that comes from our tissues. In this graph, we can see that there is a purple group, green group and red group. In the purple group, we can infer this is a the standard healthy patient, with lower blood urea levels and lower serum creatnine levels. The red group looks like high BU and high creatinin levels, indicative of someone with kidney disease. The green cluster looks like a mix of lower creatnine but slightly higher BU, this is indicative of someone at risk or strating to develop kidney complications.

#**4.** Based on the coefficients, which of the following variables is the strongest predictor of having kidney disease (age, bp (blood pressure), pot (Potassium), diabetes)?
"""

# Based on the coefficients, which of the following variables is the strongest predictor of having kidney disease ( age, bp, pot, diabetes)?
pred=["age","bp","pot","diabetes.yes"]

Xnew=combined_df[pred]
ynew=combined_df["ckd"]

#z-score
zscore= StandardScaler()
Xnew[pred] = zscore.fit_transform(Xnew)


#create and fit the new model
model = LogisticRegression()
model.fit(Xnew,ynew)

# make df with coefficients
coef = pd.DataFrame({"Coefs": model.coef_[0],
                     "predictors": pred})
coef = coef.append({"Coefs": model.intercept_[0],
                    "predictors": "intercept"}, ignore_index = True)
coef


# make confusion matrix
print(plot_confusion_matrix(model, Xnew, ynew))

# make a bar graph to show which variable is the strongest predictor of chronic kidney disease. 
print(ggplot(coef[0:4], aes(x="predictors", y="Coefs", fill = "predictors"))+geom_bar(stat="identity")+
 theme_minimal()+labs(title= "strongest predictor of having CKD", x="Predictors", y="Coeffiecient")+
 theme(panel_grid_minor_y=element_blank(),
      panel_grid_major_x=element_blank(),
      plot_title = element_text (size=20),
      legend_position = "none"))

"""## Answer to Question 4: 
I created a confusion matrix to see if my model is accurate or not. The confusion matrix shows that my model did a pretty good job at accurately predicting chronic kidney disease. It did a phenomenal job at predicting the true negatives. It predicted that 191 were true negatives. It also predicted the true positives pretty well because it predicted that 100 were true positives. I say that this model is accurate because it only classified the data incorrectly by a small amount in comparison to the amount it classified the data correctly. It only predicted 74 false positives and 35 false negatives. 

Based on the bar plot I created, diabetes is the strongest predictor of whether someone has chronic kidney disease or not. If you look at the graph, the coefficients are on the Y-axis, and the predictors are on the X-axis. Looking at the graph, it is evident that diabetes has the strongest impact because it has the highest coefficient. It also has the tallest "bar." Diabetes has a coefficient of .86 while all the other predictors have a coefficient of less than or equal to .40. Therefore, out of the predictors age, blood pressure, diabetes, and potassium, diabetes has the most impact on whether or not someone has chronic kidney disease.

#**5.** What can the characteristics of these clusters tell us about the general state of the person’s health aside from kidney disease? Will there be any irregularities?

## KMeans
"""

#(Clustering) What can the characteristics of these clusters tell us about the general state of the person’s health aside from kidney disease? Will there be any irregularities?

#KMeans
#all variables except categorical are used

variables = ['bp','bgr','bu','sc','sod','pot','hemo','age','pcv','wc', 'rc']
X = combined_df[variables]

zscore = StandardScaler()

X[variables] = zscore.fit_transform(X[variables].astype(str))

X[variables] = zscore.fit_transform(X[variables])

ks = [2,3,4,5,6,7,8,9,10]
sse = []
sils = []

for k in ks:
  km = KMeans(n_clusters = k)
  km.fit(X[variables])

  sse.append(km.inertia_)
  sils.append(silhouette_score(X[variables], km.predict(X[variables])))

sse_df = pd.DataFrame({"K": ks, "SSE": sse, "Silhouette": sils})
(ggplot(sse_df, aes(x = "K", y = "SSE")) + geom_point() + geom_line() + theme_minimal() +
labs(title = "SSE for Different Ks"))

"""This graph shows the sum of squared distance between the center of the cluster and the other points in the cluster. The graph is telling me that 4 is the best number of clusters to use for the KMeans model."""

(ggplot(sse_df, aes(x = "K", y = "Silhouette")) + geom_point() + 
geom_line() + 
theme_minimal() + 
labs(title = "Silhouette Score for Different Ks"))

"""This graph shows the sihouette score or the number that tells us how relative a point is to the cluster or group. The graph is confirming that 4 is the best number of clusters to use for the KMeans model.This graph and the graph above are used to help me with determining what amount of Ks or groups the data points should be put in."""

# Looking at these two graphs, 4 is the optimal # of K which has a decent silhouette score and a lower SSE
 # km model
km = KMeans(n_clusters = 4)
km.fit(X[variables])

membership1 = km.predict(X[variables])

X["cluster"] = membership1

combined_df["cluster"] = km.predict(X[variables])

silhouette_score(X[variables], membership1)

# sil_points
sil_points = silhouette_samples(X[variables], membership1)

# add silhouette scores and clusters to X
X["sil"] = sil_points
X["cluster"] = membership1

# sort X by cluster and silhouette score just to look better
X = X.sort_values(by = ["cluster", "sil"], ascending = True)

# number rows for graphing
X["number"] = range(0,X.shape[0])

(ggplot(X, aes(x = "number", y = "sil", fill = "factor(cluster)"))
+ geom_bar(stat = "identity") + 
 geom_hline(yintercept = np.mean(sil_points), linetype = "dashed") +
theme_minimal() + 
labs(x = "", y = "Silhouette Score", title = "Silhouette Scores") + 
theme(axis_text_x= element_blank(),
panel_grid_major_x= element_blank(),
panel_grid_minor_x= element_blank(),
legend_position= "bottom") +
scale_fill_discrete(name = "Cluster"))

"""This graph shows the sihouette score or the number that tells us how relative each point is to the cluster or group that they are in."""

for p in variables:
    combined_df[variables] = combined_df[variables].astype(float)
    print(ggplot(combined_df, aes(x = "factor(cluster)", y = p,
                             fill = "factor(cluster)")) +
         geom_boxplot() + theme_minimal() + 
         labs(title = p))

"""These 11 graphs gives us insight on the patients' health and whether they should get themselves checked out by a doctor or not. Each variable shows us the levels of each group of paitents and will give us a general diagnosis if each one is put together by a doctor. Because the graphs name is in acronyms this is what each one means in order from top to bottom: bp(Blood Pressure), bgr(Blood Glucose Random), bu(Blood Urea), sc(Serum Creatinine), sod(Sodium), pot(Potassium), hemo(Hemoglobin), age (in years),pcv(Packed Cell Volume), wc(White Blood Cell Count), rc(Red Blood Cell Count)

## Answer to Question 5: 
Before looking at the result for KMeans, for those that don't have a medical backgroud, here is the best explanation I can give for each variable. **Blood Pressure (bp)** "is the pressure of blood pushing against the walls of your arteries. Arteries carry blood from your heart to other parts of your body" (CDC). **Blood Glucose Random (bgr)** is a random glucose test that measures the amount of glucose or sugar circulating in a person’s blood (Medical News Today). **Blood Urea (bu)** "a waste product that your kidneys remove from your blood" (Medline Plus). **Serum Creatinine (sc)** is a test for creatinine in your blood. "Creatinine is a waste product in your blood that comes from your muscles. Healthy kidneys filter creatinine out of your blood through your urine. Your serum creatinine level is based on a blood test that measures the amount of creatinine in your blood. It tells how well your kidneys are working" (American Kidney Fund). **Sodium (sod)** is needed "to conduct nerve impulses, contract and relax muscles, and maintain the proper balance of water and minerals", but only a small amount of it is needed (The Nutrition Source). **Potassium's (pot)** "main role in the body is to help maintain normal levels of fluid inside our cells" (The Nutrition Source). **Hemoglobin (hemo)** "is a protein in your red blood cells that carries oxygen to your body's organs and tissues and transports carbon dioxide from your organs and tissues back to your lungs" (Mayo Clinic). **Age** is years is just the age of the person in the data. **Packed Cell Volume (pcv)** "is a measurement of the proportion of blood that is made up of cells" (Lab Tests Online). **White blood cell count (wc)** "measures the number of white cells in your blood. White blood cells are part of the immune system. They help your body fight off infections and other diseases" (Medline Plus). **Red Blood Cell Count (rc)** "measures the number of red blood cells, also known as erythrocytes, in your blood. Red blood cells carry oxygen from your lungs to every cell in your body. Your cells need oxygen to grow, reproduce, and stay healthy" (Medline Plus).

In the beginnning to find k or the number of clusters/groups I wanted to make, I used the the sum of the squared Euclidean distances of each point to its closest centroid, which also means how far a distance it is between the center of the cluster and the other data points in the cluster. I also used a silloutte score graph or in other words a graph that has the number that tells us the average of how relative a point is to the cluster or group for that specifc number of groups. The two graphs told me that the best number of groups to make was 4. Then I looked at a silloutte score graph for each point where in this graph it tells me how relative each point is to the group they were assigned to. This graph tells me how much I can trust the groups that were made. The higher the silohette score the farther the point and the lower scores means the point is closer to the center of the group. In general, I could slightly trust my groups of points, but not too much because a lot of the points are far away from their center point.

Looking at the results of **KMeans**, I see that there were multiple graphs made for each variable and it gave a lot of different symptoms for each cluster or group of people. There are many other different things these graphs can tell us besides the fact of whether a person has Hypertension, Diabetes Mellitus, Coronary Artery Disease, Pedal Edema, a Chronic Kidney Disease or Anemia. In the **bp** graph, people's blood pressure in cluster 0 and 2 have a good range (normal) while cluster 1 is a little low, which might mean not enough blood is getting to different parts of the body, and cluster 3 is a little high, which might mean that the heart is working too hard. In the **bgr** graph, people's blood glucose seem normal in cluster 2 while cluster 1 is a bit low, which might mean a person may have hypoglycemia, and cluster 0 and 3 are a bit high, which might mean that a person may have hyperglycemia that can increase the risk for other disease like heart disease. In the **bu** graph, people's blood urea in cluster 2 are at normal levels, while cluster 3 has high blood urea, which could mean that the kidneys are not working as they should, and clusters 0 and 1 are kinda low, which might mean that they could have a liver disease or malnutrition. In the **sc** graph, people's serum cretinine in cluster 2 seems normal again while cluster 3 is a little high, which might mean that the kidneys are functioning poorly, and clusters 0 and 1 are a little low, which could mean the deterioration of muscle or muscular dystrophy. In the **sod** graph, people's sodium levels for cluster 0 seem to look normal, while cluster 2 seems a little low, which is not good because if it drops any lower then they might have hyponatremia, and for clusters 1 and 3, they seem a little high which might mean dehydration. In the **pot** graph, people's potassium levels in cluster 0, 1, and 2 seem normal while cluster 3 is relly high, which could mean kidney disease or dehydration. In the **hemo** graph, people's hemoglobin levels in cluster 0 seem close to normal, while cluster 1 is a little high, which could mean the person is fatiuged or have dizziness, as for clusters 2 and 3 they seem a bit low, which could mean your body is not getting enoguh oxygen. The **age** graph could be a good inticator as to why some people have certain symptoms like cluster 1 and 3 could be old, cluster 2 could be middle age, and cluster 1 could be the younger ones. In the **pcv** graph, people's packed cell volume is normal in cluster 1, while clusters 0, 2, and 3 seem a bit low which could mean those people may have anemia. In the **wc** graph, people's white blood cell count in clusters 0, 1, and 2 seem to be at normal levels, while cluster 3 might a little low but not dangerous, however having a low cell count could make the person suspectible to infections. In the **rc** graph, people's red blood cell count in clusters 0 and 1 seem to be at normal levels, while clusters 2 and 3 are a little low, which could mean the person has anemia. All the inferences I made on the symptoms were researched on google. I looked at why might it be bad if one thing was too low or too high.

In general for all graphs we want each variable to be at normal levels because having too much or too little of something could be bad for the person. This does not count age because age is a natural thing that happens in life. Also I might have overreacted on some of the graphs because not everyone is a perfect human being with normals levels in everything. As long as the variables don't reach drastic levels then the person will be fine. Furthermore, I think the only irregularity that I saw came from potassium because cluster 3's levels were so high compared to the other clusters. In the other graphs there was only slight increases or decreases.

#**6.** Which variables will have the largest impact on determining kidney disease when penalized?

## LASSO
"""

#(Dimensionality reduction model) Which variables will have the largest impact on determining kidney disease when penalized?

#LASSO
var = ['bp','bgr','bu','sc','sod','pot','hemo','age','pcv','wc', 'rc','sg','al','su','bacteria.present','heart_disease.yes','anemia.yes','pedaledema.yes','diabetes.yes','appetite.good', 'appetite.poor','hyptertension.yes','puscellclumps.present','puscell_level.abnormal']
X = combined_df[var]
y = combined_df["ckd"]

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2,random_state = 1234)

zz = StandardScaler()

X_train[var] = zz.fit_transform(X_train[var])
X_test[var] = zz.transform(X_test[var])

#model
lsr = Lasso()

lsr.fit(X_train,y_train)

print("TRAIN MAE: ", mean_absolute_error(y_train, lsr.predict(X_train)))
print("TEST MAE: ", mean_absolute_error(y_test, lsr.predict(X_test)))

print("TRAIN R2: ", r2_score(y_train, lsr.predict(X_train)))
print("TEST R2 : ", r2_score(y_test, lsr.predict(X_test)))

lsr_tune = LassoCV(cv = 5).fit(X_train,y_train)
print("\nwe chose " + str(lsr_tune.alpha_) + " as our alpha.")

lr = LogisticRegression()

lr.fit(X_train,y_train)

print("TRAIN: ", r2_score(y_train, lr.predict(X_train)))
print("TEST : ", r2_score(y_test, lr.predict(X_test)))

#Logistic
lr_np = LogisticRegression(penalty = "none")

lr_np.fit(X_train, y_train)

lr_np.coef_

print("No penalty:",lr_np.coef_ )
#Lasso
lr_l = LogisticRegression(penalty = "l1", solver = "liblinear")

lr_l.fit(X_train, y_train)

lr_l.coef_

print("Lasso pentalty:",lr_l.coef_ )

DF = pd.DataFrame({"conames": var,
                      "coefs_lasso": lr_l.coef_.flatten(),
                      "coefs_logistic": lr_np.coef_.flatten()})
DF

"""This table gives a comparison between the coeffients for the LASSO model and the coeffients for the Logistic Regression model. The LASSO model gives the Logistic Regression model a penalty which makes it LASSO. Coeffients tell us how much the mean of the variable we are predicting changes given a one-unit shift in the a predictor variable while holding other variables in the model constant."""

df = pd.DataFrame({"conames": var,
                      "coefs": lr_l.coef_.flatten()})

(ggplot(df, aes(x = "conames",
                y = "coefs", fill = "conames")) +
  geom_bar(stat = "identity") + ggtitle("All Coefficients") + theme_minimal()+
 labs(x = "Variables", y = "Coefficient") +
 theme(panel_grid_minor_y = element_blank(), 
       panel_grid_major_x = element_blank(),
       axis_title_x = element_text (size = 12),
       plot_title = element_text (size = 15),
       axis_text_x = element_text(angle = 90)))

"""This graph shows the LASSO coeffiecients. This graph is telling us that the most impactful coeffiecint on determining if someone has chronic kidney disease or not is hemoglobin. Coeffients tell us how much the mean of the variable we are predicting changes given a one-unit shift in the a predictor variable while holding other variables in the model constant."""

(ggplot(combined_df, aes(x ="hemo", y ="ckd")) +
  geom_point(color = "blue", shape = 10) + ggtitle("Relationship between Hemoglobin and Chronic Kidney Disease") + theme_minimal()+
 labs(x = "Hemoglobin", y = "Chronic Kidney Disease") +
 theme(panel_grid_minor_y = element_blank(), 
       panel_grid_major_x = element_blank(),
       axis_title_x = element_text (size = 12),
       plot_title = element_text (size = 15),
       legend_position = "none"))

"""Because hemoglobin was the most impactful variable on whether someone had kidney disease or not, this graph shows the relationship between Hemoglobin and those who did or didn't get Chronic Kidney Disease.

## Answer to Question 6: 
Looking at the results from the LASSO model, the variables that will have the largest impact on determining kidney disease when penalized is Hemoglobin, Potassium, Specific Gravity, and Albumin. The reason is because looking at the graph that show the coefficients of all the differetn variables, it is clear that the variables that I just mentioned have a higher coeffient than the rest of the variables. Furthermore it is important to disregard the negative and positive sign of the coefficents because it doesn't matter when finding the most impactful variable. The only thing that matters is the coeffient number, since that is what tells us the impact of the number. Anyways, a coeffients tell us how much the mean of the variable we are predicting changes given a one-unit shift in the a predictor variable while holding other variables in the model constant. This means that changes in either Hemoglobin, Potassium, Specific Gravity, or Albumin will greatly affect whether a person gets a Chronic Kidney Disease or not. This means that these 4 variables are the ones we should pay close attention to when determining whether a person has a kidney disease or not. Also the graph that shows the relationship between Hemoglobin which is the strongest predictor and Chronic Kidney Disease is an example of how the variable affects the result on the whether a person will get a Chronic Kidney Disease or not. 

Furthermore, for those that don't have a medical backgroud, here is the the best explanation I can give for each impactful variable. **Hemoglobin (hemo)** "is a protein in your red blood cells that carries oxygen to your body's organs and tissues and transports carbon dioxide from your organs and tissues back to your lungs" (Mayo Clinic). **Potassium's (pot)** "main role in the body is to help maintain normal levels of fluid inside our cells" (The Nutrition Source). **Specific Gravity (sg)** is used to tell the concentration of your urine (healthmatter.io). **Albumin's (al)** important role is "keeping the fluid in the blood from leaking into the tissues" (Mount Sinai). Albumin is also made in the liver.
"""

#coding for the pdf version
# Download as PDF with Jupyter Notebook

# doesn't show this cells output when downloading PDF
!pip install gwpy &> /dev/null

# installing necessary files
!apt-get install texlive texlive-xetex texlive-latex-extra pandoc
!sudo apt-get update
!sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-plain-generic

# installing pypandoc
!pip install pypandoc

# connecting your google drive
from google.colab import drive
drive.mount('/content/drive')

# copying your file over. Change "Class6-Completed.ipynb" to whatever your file is called (see top of notebook)
!cp "drive/My Drive/Colab Notebooks/Final Project part 5.ipynb" ./

# Again, replace "Class6-Completed.ipynb" to whatever your file is called (see top of notebook)
!jupyter nbconvert --to PDF "Final Project part 5.ipynb"