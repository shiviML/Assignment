from helpers import calculate_total_seconds,calculate_average_seconds,\
compute_unique_actions,count_sessions,count_unique_actions
import pandas as pd
import pickle
import numpy as np
import os


class Predictor:
    """
    A class for predicting user destination based on user and session data.

    Attributes:
         users_df (DataFrame): DataFrame containing user data.
         sessions_df (DataFrame): DataFrame containing session data filtered to include only relevant users.
    """
    def __init__(self,users_df):
        """
         Initializes the Predictor with user data and loads session data from a CSV.
        
         Args:
             users_df (DataFrame): A DataFrame containing user data.
         """
        self.users_df = users_df
        try:
            sessions_path = os.path.join('cache', 'sessions.csv')
            self.sessions_df = pd.read_csv(sessions_path)
        except FileNotFoundError:
            raise Exception(f"File not found: {sessions_path}")
        
        user_ids = set(self.users_df['id'])
        self.sessions_df = self.sessions_df[self.sessions_df['user_id'].isin(user_ids)]

    def preprocess(self,tfidf_vectorizers,count_vectorizer,one_hot_encoders,final_columns):
        """
         Preprocesses the user and session dataframes by applying vectorization and encoding techniques.
        
         Args:
             tfidf_vectorizers (list): List of dictionaries containing tfidf vectorizers and their target columns.
             count_vectorizer (dict): Dictionary containing a count vectorizer and its target column.
             one_hot_encoders (list): List of dictionaries containing one-hot encoders and their target columns.
             final_columns (list): List of columns to retain in the final DataFrame.
        
         Returns:
             DataFrame, Series: The preprocessed DataFrame and user_id Series.
         """
        
        # Fix age outliers
        self.users_df[self.users_df['age'] < 18]['age'] = 18
        self.users_df[self.users_df['age'] > 120]['age'] = 120
        
        # Replace '-unknown-' with NaN
        self.users_df.replace('-unknown-', np.nan,inplace=True)
        self.sessions_df.replace('-unknown-', np.nan,inplace=True)

        # Aggregate session data
        df_unique_sessions=self.sessions_df.groupby(["user_id"],as_index=False).agg(lambda x :x.tolist())
        
        # Compute aggregated features
        df_unique_sessions["sum_secs_elapsed"]=df_unique_sessions["secs_elapsed"].apply(calculate_total_seconds)
        df_unique_sessions["avg_seconds_elapsed"]=df_unique_sessions["secs_elapsed"].apply(calculate_average_seconds)
        df_unique_sessions["count_sessions"]=df_unique_sessions["secs_elapsed"].apply(count_sessions)
        df_unique_sessions['unique_action'] = df_unique_sessions['action'].apply(compute_unique_actions)
        df_unique_sessions['unique_action_type'] = df_unique_sessions['action_type'].apply(compute_unique_actions)
        df_unique_sessions['unique_action_detail'] = df_unique_sessions['action_detail'].apply(compute_unique_actions)
        df_unique_sessions['unique_device_type'] = df_unique_sessions['device_type'].apply(compute_unique_actions)
        df_unique_sessions["number_unique_actions_type"]=df_unique_sessions["action_type"].apply(count_unique_actions)
        df_unique_sessions["number_unique_action"]=df_unique_sessions["action"].apply(count_unique_actions)
        df_unique_sessions["number_unique_actions_detail"]=df_unique_sessions["action_detail"].apply(count_unique_actions)
        df_unique_sessions["number_unique_device_type"]=df_unique_sessions["device_type"].apply(count_unique_actions)

        # Merge user and session data
        df = self.users_df.merge(df_unique_sessions, left_on = 'id', right_on = 'user_id', how = 'inner')

        # Apply vectorization
        tfidf_df = [pd.DataFrame(vec['vectorizer'].transform(df[vec['for']].values).toarray(), 
                                 columns=vec['vectorizer'].get_feature_names()) for vec in tfidf_vectorizers]
        cv_df = pd.DataFrame(count_vectorizer['vectorizer'].transform(df[count_vectorizer['for']].values).toarray(), 
                             columns=count_vectorizer['vectorizer'].get_feature_names())
        

        df = pd.concat([df.reset_index(drop = True)] + tfidf_df + [cv_df] ,axis=1)

        # Apply one-hot encoding
        for one_hot_encoder in one_hot_encoders:
            cat = one_hot_encoder['for']
            encoder = one_hot_encoder['encoder']
            X = df[cat].fillna('FEMALE').values.reshape(-1,1) ### Modified here
            X = encoder.transform(X).toarray()
            X = pd.DataFrame(X, columns = encoder.get_feature_names([cat]))
            df = pd.concat([df,X],axis=1)

        user_id = df['user_id']

        # Drop unnecessary columns
        initial_columns = set(df.columns.to_list())
        cols_to_drop = list(initial_columns - set(final_columns))
        df.drop(cols_to_drop, axis=1,inplace=True)

        if df.shape[1] != len(final_columns):
            raise ValueError("The final DataFrame does not match the expected number of columns.")


        return df,user_id
    
    def predict(self,classifier,df,label_encoder,user_id):
        """
         Predicts the destination country for users and prints results.
        
         Args:
             classifier (Model): A trained classification model.
             df (DataFrame): The DataFrame to predict on.
             label_encoder (LabelEncoder): Encoder for decoding labels.
             user_id (Series): Series of user IDs corresponding to predictions.
        
         Returns:
             list of dicts: A list of dictionaries containing user IDs and their predicted destinations.
        """

        predictions = classifier.predict(df.fillna(0))  ## changed to fillna
    
        decoded_predictions = label_encoder.inverse_transform(predictions)

        results = [
            {"user_id": uid, "country_destination": pred}
            for uid, pred in zip(user_id, decoded_predictions)
        ]

        return results



