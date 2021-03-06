import pandas as pd 
from datetime import datetime 
import datetime as dt  
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def impute_dataframe(df, features=[], features_except=False, impute_numeric=None, impute_categorical=None, impute_map={}):      
    df1 = df.copy()   
    
    feat_null = pd.DataFrame({'feat':df1.columns.values,'type':df1.dtypes})     
    feat_null = feat_null.loc[df1.isnull().sum()>0,:] 
    
    if ((type(features)==list) & len(features)>0):         
        if not(features_except):             
            feat_null = feat_null.loc[[fe for fe in feat_null.index.values if (fe in features)],:]         
        else:   
            feat_null = feat_null.loc[[fe for fe in feat_null.index.values if not(fe in features)],:]      
    
    for c in feat_null.index.values:         
        if c in impute_map:             
            if feat_null.loc[c,'type'] in ['int','int64','float','float64']:                 
                if type(impute_map[c])==str:                     
                    df1[c] = df1[c].fillna(df1[c].quantile(int(impute_map[c].replace('q',''))*0.01))
                else:                     
                    df1[c] = df1[c].fillna(impute_map[c])  
            else:   
                df1[c] = df1[c].fillna(impute_map[c])  
                
        elif feat_null.loc[c,'type']=='O':             
            if (impute_categorical==None):  
                df1[c] = df1[c].fillna("Unknown")             
            elif impute_categorical=='mode':
                df1[c] = df1[c].fillna(df1[c].mode()[0])             
            else:   
                df1[c] = df1[c].fillna(impute_categorical)          
        elif feat_null.loc[c,'type'] in ['int','int64','float','float64']: 
            if ((impute_numeric==None)|impute_numeric=='median'):  
                df1[c] = df1[c].fillna(df1[c].median()) 
            elif impute_numeric=='mean':
                df1[c] = df1[c].fillna(df1[c].mean())  
            elif type(impute_numeric)==str: 
                df1[c] = df1[c].fillna(df1[c].quantile(int(impute_numeric.replace('q',''))*0.01))  
            else:  
                df1[c] = df1[c].fillna(impute_numeric) 
    
    return df1  

def get_time_distance(x_start, x_end, distance=None):  
    dist = x_end - x_start     
    if ((distance=='days')|(distance==None)):  
        return dist.days
    elif (distance=='months'): 
        return dist.days / 30.0
    elif (distance=='years'): 
        return dist.days / 365.25 
    elif (distance=='seconds'):
        return dist.total_seconds()
    elif (distance=='minutes'):
        return dist.total_seconds() / 60.0 
    elif (distance=='hours'): 
        return dist.total_seconds() / 3600.00     
    return dist.days  

def transform_datetime(df, features=[], ts_format='%Y-%m-%d', ts_target=None): 
    # ts_format: ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']   
    
    df1 = df.copy()      
    
    feat_typ = pd.DataFrame({'feat':df1.columns.values,'type':df1.dtypes}) 
    feat_typ = feat_typ.loc[features,:]          
    ts_target = datetime.now() if (ts_target==None) else datetime.strptime(ts_target, ts_format)          
    
    for c in features:         
        if feat_typ.loc[c,'type']=='O':
            df1[c] = df1[c].map(lambda x: datetime.strptime(x, ts_format)) 
        df1[c] = df1.apply(lambda x: get_time_distance(x[c], ts_target, distance=None), axis=1)              
    
    return df1  

def one_hot_encoding(df, features=[], features_except=False, cat_map={}, drop_old=True, replace_space=' '):
    df1 = df.copy() 
    
    feat_typ = pd.DataFrame({'feat':df1.columns.values,'type':df1.dtypes}) 
    feat_typ = feat_typ.loc[feat_typ.loc[:,'type']=='O',:]  
    
    if ((type(features)==list) & len(features)>0):         
        if not(features_except):             
            feat_typ = feat_typ.loc[[fe for fe in feat_typ.index.values if    (fe in features)],:]  
        else:  
            feat_typ = feat_typ.loc[[fe for fe in feat_typ.index.values if not(fe in features)],:]          
            
    for c in feat_typ.index.values:
        df1[c] = df1[c].map(lambda x: x if x==None else x.replace(' ',replace_space))
        if c in cat_map:             
            list_feat = cat_map[c]             
            for col in list_feat:                 
                df1["{}_{}".format(c,col)] = df1[c].map(lambda x: 1 if (x.strip()==col) else 0)                      
        else:             
            t = pd.get_dummies(df1[c])             
            t.columns = ['{}_{}'.format(c,col) for col in t.columns.values]             
            df1 = pd.concat([df1, t], axis=1)             
            if drop_old:                 
                df1 = df1.drop(c, axis=1)                      
    return df1

def plot_hist(df, feature, target, lt=None, lte=None, gt=None, gte=None, ltq=1.0, gtq=0.0):

    data = df.copy()
    # data[target] = Y
    # data[feature] = np.log1p(data[feature])
    data = data.loc[data[feature]<=data[feature].quantile(ltq),:]
    data = data.loc[data[feature]>=data[feature].quantile(gtq),:]
    if lt!=None:
        data = data.loc[data[feature]<lt,:]
    if gt!=None:
        data = data.loc[data[feature]>gt,:]
    if lte!=None:
        data = data.loc[data[feature]<=lte,:]
    if gte!=None:
        data = data.loc[data[feature]>=gte,:]
    fig, ax = plt.subplots()
    _ = sns.distplot(data.loc[data[target]==1,feature].dropna(), ax=ax, color='red')
    _ = sns.distplot(data.loc[data[target]==0,feature].dropna(), ax=ax, color='green')
    
def plot_bar(df, feature, target):

    data = df.copy()
    # data[target] = Y
    df_cnt = (data.groupby([feature])[target]
                         .value_counts(normalize=True)
                         .rename('percentage')
                         .mul(100)
                         .reset_index()
                         .sort_values('percentage')
             )
    df_cnt = df_cnt.loc[df_cnt[target]==1,:]
    df_cnt = df_cnt.sort_values(by="percentage", ascending=False).reset_index(drop=True)
    ax = sns.barplot(x=feature, y="percentage", hue=target, data=df_cnt, order=df_cnt[feature])
    _ = ax.set_xticklabels(ax.get_xticklabels(),rotation=60)
    # df_feat[feature] = df_cnt.copy()
    # df_cnt.sort_values(by="percentage")

def make_confusion_matrix(cf,
                          group_names=None,
                          categories='auto',
                          count=True,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          sum_stats=True,
                          figsize=None,
                          cmap='Blues',
                          title=None):
    '''
    This function will make a pretty plot of an sklearn Confusion Matrix cm using a Seaborn heatmap visualization.
    Arguments
    ---------
    cf:            confusion matrix to be passed in
    group_names:   List of strings that represent the labels row by row to be shown in each square.
    categories:    List of strings containing the categories to be displayed on the x,y axis. Default is 'auto'
    count:         If True, show the raw number in the confusion matrix. Default is True.
    normalize:     If True, show the proportions for each category. Default is True.
    cbar:          If True, show the color bar. The cbar values are based off the values in the confusion matrix.
                   Default is True.
    xyticks:       If True, show x and y ticks. Default is True.
    xyplotlabels:  If True, show 'True Label' and 'Predicted Label' on the figure. Default is True.
    sum_stats:     If True, display summary statistics below the figure. Default is True.
    figsize:       Tuple representing the figure size. Default will be the matplotlib rcParams value.
    cmap:          Colormap of the values displayed from matplotlib.pyplot.cm. Default is 'Blues'
                   See http://matplotlib.org/examples/color/colormaps_reference.html
                   
    title:         Title for the heatmap. Default is None.
    '''


    # CODE TO GENERATE TEXT INSIDE EACH SQUARE
    blanks = ['' for i in range(cf.size)]

    if group_names and len(group_names)==cf.size:
        group_labels = ["{}\n".format(value) for value in group_names]
    else:
        group_labels = blanks

    if count:
        group_counts = ["{0:0.0f}\n".format(value) for value in cf.flatten()]
    else:
        group_counts = blanks

    if percent:
        group_percentages = ["{0:.2%}".format(value) for value in cf.flatten()/np.sum(cf)]
    else:
        group_percentages = blanks

    box_labels = [f"{v1}{v2}{v3}".strip() for v1, v2, v3 in zip(group_labels,group_counts,group_percentages)]
    box_labels = np.asarray(box_labels).reshape(cf.shape[0],cf.shape[1])


    # CODE TO GENERATE SUMMARY STATISTICS & TEXT FOR SUMMARY STATS
    if sum_stats:
        #Accuracy is sum of diagonal divided by total observations
        accuracy  = np.trace(cf) / float(np.sum(cf))

        #if it is a binary confusion matrix, show some more stats
        if len(cf)==2:
            #Metrics for Binary Confusion Matrices
            precision = cf[1,1] / sum(cf[:,1])
            recall    = cf[1,1] / sum(cf[1,:])
            f1_score  = 2*precision*recall / (precision + recall)
            stats_text = "\n\nAccuracy={:0.3f}\nPrecision={:0.3f}\nRecall={:0.3f}\nF1 Score={:0.3f}".format(
                accuracy,precision,recall,f1_score)
        else:
            stats_text = "\n\nAccuracy={:0.3f}".format(accuracy)
    else:
        stats_text = ""


    # SET FIGURE PARAMETERS ACCORDING TO OTHER ARGUMENTS
    if figsize==None:
        #Get default figure size if not set
        figsize = plt.rcParams.get('figure.figsize')

    if xyticks==False:
        #Do not show categories if xyticks is False
        categories=False


    # MAKE THE HEATMAP VISUALIZATION
    plt.figure(figsize=figsize)
    sns.heatmap(cf,annot=box_labels,fmt="",cmap=cmap,cbar=cbar,xticklabels=categories,yticklabels=categories)

    if xyplotlabels:
        plt.ylabel('Actual label')
        plt.xlabel('Predicted label' + stats_text)
    else:
        plt.xlabel(stats_text)
        