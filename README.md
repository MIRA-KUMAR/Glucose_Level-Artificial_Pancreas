# Glucose_Level-Artificial_Pancreas

# Steps to Execute Code:

1. Import all the necessary libraries required to run the code.
2. Read the input data (using pandas) as a dataframe
3. Create a new column for timestamp by merging the Date and Time columns in the original data.
4. Extract the timestamp of when the manual mode ends and the auto mode begins from the insulin data.
5. Using the extracted timestamp, create dataframes for auto mode and manual mode.
6. Prepare new dataframes for overnight and daytime data.
7. Calculate all the metrics for the created datasets and store its calculation in a new dataframe.
8. Export the result dataframe into Results.csv without the index and the header using a built-in function provided by pandas.

Configuration & Packages Used:

        - Python === 3.7.6
        - Pandas === 0.25.1
        - Datetime === (built-in)
