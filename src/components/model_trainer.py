import os
import sys
from dataclasses import dataclass

from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_models
# from src.components.data_transformation import DataTransformation

@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'model.pkl')
    
class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        
    def initiate_model_trainer(self, train_array, test_array):
        try:
            logging.info("Splitting training and test input data")
            X_train, y_train, X_test, y_test = (
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]
            )
            
            models = {
                "Random Forest" : RandomForestRegressor(),
                "Decision Tree Regressor" : DecisionTreeRegressor(),
                "Gradient Boosting Regressor" : GradientBoostingRegressor(),
                "Linear Regression" : LinearRegression(),
                "K-Neighbours Regressor" : KNeighborsRegressor(),
                "XGBoost Regressor" : XGBRegressor(),
                "CatBoost Regressor" : CatBoostRegressor(verbose=False),
                "AdaBoost Regressor" : AdaBoostRegressor()
            }
            
            model_report : dict = evaluate_models(X_train = X_train, 
                                                  y_train = y_train, 
                                                  X_test = X_test, 
                                                  y_test = y_test,
                                                  models = models)


            # to get best model score from dictionary
            best_model_score = max(sorted(model_report.values()))
            
            # to get the best model name from dict
            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model = models[best_model_name]
            
            if best_model_score < 0.6:
                raise CustomException('No best model found')
            logging.info(f"Best found model on both training and testing dataset")
            
            save_object(file_path=self.model_trainer_config.trained_model_file_path, obj=best_model)
            
            predicted = best_model.predict(X_test)
            r2Score = r2_score(y_test, predicted)

            return r2Score
        
        except Exception as e:
            raise CustomException(e, sys)