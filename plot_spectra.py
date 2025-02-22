import requests # Import the requests library to make HTTP requests
import matplotlib.pyplot as plt # Import the matplotlib library to plot data

# Define the base URL of your Flask application
base_url = 'http://127.0.0.1:5001' 

# Function to fetch data from a given endpoint
def fetch_data(endpoint):
    # Make a GET request to the endpoint
    response = requests.get(f'{base_url}/{endpoint}')
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Check if the response was successful
        if data['success']:
            # Extract the x and y values from the response
            x_values = [float(x) for x in data['x']]
            y_values = [float(y) for y in data['y']]
            # Return the x and y values
            return x_values, y_values
        else:
            # Print the error message from the server
            print(f"Error from server: {data['text']}")
    else:
        # Print the error message if the request failed
        print(f"Failed to fetch data: {response.status_code}")
    # Return empty lists if the request failed
    return [], []

# Fetch data from /test endpoint
# x_test, y_test = fetch_data('test')

# Fetch data from /test_clean endpoint
x_test_clean, y_test_clean = fetch_data('test_clean')

# Plotting the data
plt.figure(figsize=(12, 6))

# Plot for /test endpoint
# Create a subplot with 1 row and 2 columns
## plt.subplot(1, 2, 1)
# Plot the processed spectrum
## plt.plot(x_test, y_test, label='Processed Spectrum')
# Add title, labels, and legend
## plt.title('Processed Spectrum from /test')
# Set the x and y labels
## plt.xlabel('Wavenumber (cm⁻¹)')
# Set the y label
## plt.ylabel('Transmittance')
# Add a legend to the plot
## plt.legend()

# Plot for /test_clean endpoint
plt.subplot(1, 2, 2)
plt.plot(x_test_clean, y_test_clean, label='Raw Spectrum', color='orange')
plt.title('Raw Spectrum from /test_clean')
plt.xlabel('Frequency (GHz)')
plt.ylabel('Intensity')
plt.legend()

plt.tight_layout()
plt.show()
