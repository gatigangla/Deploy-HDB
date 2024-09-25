import streamlit as st
import pandas as pd
from pycaret.regression import *

# Load your trained PyCaret model
model = load_model('best_model')  # Replace 'best_model' with the actual model filename if different

# Load the dataset to get column names
data = pd.read_csv('X_train_transformed.csv')  # Ensure you have the correct path

# Create a dictionary to map dummy variable groups to their base inputs
dummy_mappings = {
    'region': ['region_Central', 'region_East', 'region_North', 'region_Others', 'region_West'],
    'flat_model': ['flat_model_2-room', 'flat_model_Adjoined flat', 'flat_model_Apartment', 'flat_model_DBSS', 
                   'flat_model_Improved', 'flat_model_Improved-Maisonette', 'flat_model_Maisonette', 
                   'flat_model_Model A', 'flat_model_Model A-Maisonette', 'flat_model_Model A2', 
                   'flat_model_Multi Generation', 'flat_model_New Generation', 'flat_model_Premium Apartment', 
                   'flat_model_Premium Apartment Loft', 'flat_model_Premium Maisonette', 'flat_model_Simplified', 
                   'flat_model_Standard', 'flat_model_Terrace', 'flat_model_Type S1', 'flat_model_Type S2'],
    'storey_category': ['storey_category_1-5', 'storey_category_6-10', 'storey_category_11-15', 
                        'storey_category_16-20', 'storey_category_21-25', 'storey_category_26-30', 
                        'storey_category_31-35', 'storey_category_36-40', 'storey_category_41-45', 
                        'storey_category_46-50', 'storey_category_>50']
}

# Move user inputs to the sidebar
tranc_year_month = st.sidebar.text_input('Transaction Year-Month', '2024-01')
town = 'Example Town' #st.sidebar.text_input('Town', 'Example Town')
flat_type = st.sidebar.selectbox('Flat Type', ['1 Room', '2 Room', '3 Room', '4 Room', '5 Room', 'Executive', 'Multi-Generation'])

hdb_age = st.sidebar.number_input('HDB Age (years)', min_value=0, max_value=99, value=20)
total_dwelling_units = st.sidebar.number_input('Total Dwelling Units', min_value=1, value=100)
remaining_lease = st.sidebar.number_input('Remaining Lease (years)', min_value=1, value=60)

# Move amenities to the sidebar
st.sidebar.subheader("Amenities within 1km")
mall_nearby = st.sidebar.checkbox('Mall')
hawker_nearby = st.sidebar.checkbox('Hawker')
mrt_nearby = st.sidebar.checkbox('MRT Station')
bus_stop_nearby = st.sidebar.checkbox('Bus Stop')

# Calculate amenities score
amenities_score = 0
if mall_nearby:
    amenities_score += 1
if hawker_nearby:
    amenities_score += 1
if mrt_nearby:
    amenities_score += 1
if bus_stop_nearby:
    amenities_score += 1

pri_dist_vac = st.sidebar.number_input('Primary School Distance (Vacancy)', min_value=0, value=10)

# Move dummy variable inputs to the sidebar
region = st.sidebar.selectbox('Region', dummy_mappings['region'])
flat_model = st.sidebar.selectbox('Flat Model', dummy_mappings['flat_model'])
storey_category = st.sidebar.selectbox('Storey Category', dummy_mappings['storey_category'])

# Submit button remains in the main content area
if st.sidebar.button('Submit'):
    # Ordinal mapping for flat_type
    flat_type_map = {
        '1 Room': 1,
        '2 Room': 2,
        '3 Room': 3,
        '4 Room': 4,
        '5 Room': 5,
        'Executive': 6,
        'Multi-Generation': 7
    }
    flat_type = flat_type_map[flat_type]

    # Initialize the base user input with non-dummy variables
    user_input = {
        'Tranc_YearMonth': tranc_year_month,
        'town': town,
        'flat_type': flat_type,
        'hdb_age': hdb_age,
        'total_dwelling_units': total_dwelling_units,
        'remaining_lease': remaining_lease,
        'amenities_1km': amenities_score,
        'pri_dist_vac': pri_dist_vac
    }

    # Initialize all dummy variables to 0
    input_data = {col: 0 for col in data.columns}

    # Map non-dummy inputs to the input_data dictionary
    input_data['Tranc_YearMonth'] = user_input['Tranc_YearMonth']
    input_data['town'] = user_input['town']
    input_data['flat_type'] = user_input['flat_type']
    input_data['hdb_age'] = user_input['hdb_age']
    input_data['total_dwelling_units'] = user_input['total_dwelling_units']
    input_data['remaining_lease'] = user_input['remaining_lease']
    input_data['amenities_1km'] = user_input['amenities_1km']
    input_data['pri_dist_vac'] = user_input['pri_dist_vac']

    # Map dummy variables based on user selection
    input_data[region] = 1  # region dummy variable
    input_data[flat_model] = 1  # flat_model dummy variable
    input_data[storey_category] = 1  # storey_category dummy variable

    # Convert the input_data into a DataFrame
    input_df = pd.DataFrame([input_data])

    # Handle categorical columns: Replace strings with the expected categorical codes if required
    input_df['flat_type'] = input_df['flat_type'].astype('category')
    input_df['town'] = input_df['town'].astype('category')

    # Make a prediction using the PyCaret model
    prediction = model.predict(input_df)

    # Display the prediction result
    st.success(f'The predicted resale price of the flat is ${prediction[0]:.2f}')
