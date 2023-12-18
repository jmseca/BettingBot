# Husky
From scratch ML models to predict the outcome of Football games in 7 different leagues

## Note

I implemented all this code during the COVID-19 pandemic, from Mar 2020 to Sep 2020.
Before this project, I had only done a few very simple things, so this was a big leap.

Furthermore, because I started this almost as a beginner, I had no Refactoring habits. This led to the disorganization you can see.
I plan to organize it one day.

And the comments are all in Portuguese (Pt) :(

## Examples

To facilitate, I have listed some files where you can see what I did.

| Technique | File Path |
| ----------|---------- |
| **Feature Engineering** | [ALL/AAPredictions/**Add_HUSKY6.py**](ALL/AAPredictions/Add_HUSKY6.py) |
| **Random Forest** | [ALL/AAPredictions/**Multi_DeForest_Husky_C.py**](ALL/AAPredictions/Multi_DeForest_Husky_C.py) |
| **Analysing Test Results** | [ALL/**Analyse_Husky2.ipynb**](ALL/Analyse_Husky2.ipynb) |

Below is an image of the test analysis. All values are in percentage.
- TLNN_FLMM -> NN (threshold for accepting a prediction in a tree), MM (threshold for accepting a prediction in a forest).
- Predicted_Var = 1 -> Predicting if the Home Team wins the game.
- Accurate_Predictions -> Of the games predicted as 1, how many did the model get right.
- Games_Predicted -> Percentage of games that were predicted as 1.
- Accurate_Games_Predicted -> Percentage of games that were predicted as 1 and were, in fact, 1.
 
![image](https://github.com/jmseca/BettingBot/assets/82723911/e26abefe-1821-41e3-b77c-50589d220b30)


The best results happened when 60 <= NN <= 80. You can find the entire table on [ALL/**Analyse_Husky2.ipynb**](ALL/Analyse_Husky2.ipynb)


